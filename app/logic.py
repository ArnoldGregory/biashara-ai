from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import Business, Sale, Expense, Customer, Inventory, Operator, get_user_context, generate_code

def handle_new_user(db: Session, phone: str, message: str) -> str:
    msg = message.strip()

    # joining as operator
    if msg.lower().startswith("join "):
        parts = msg.split()
        if len(parts) < 3:
            return "To join a business type: join BUSINESSCODE YourName\nExample: join STACY001 John"
        code = parts[1].upper()
        name = " ".join(parts[2:])
        business = db.query(Business).filter(Business.code == code).first()
        if not business:
            return f"❌ Business code {code} not found. Ask your owner for the correct code."
        operator = Operator(business_id=business.id, phone=phone, name=name)
        db.add(operator)
        db.commit()
        return f"✅ Welcome {name}! You've joined *{business.name}*.\nYou can now record sales for this business."

    # registering as owner
    business = Business(
        phone=phone,
        name=msg,
        code=generate_code(msg)
    )
    db.add(business)
    db.commit()
    db.refresh(business)
    return (
        f"✅ Welcome to Biashara AI!\n\n"
        f"Business: *{business.name}*\n"
        f"Your code: *{business.code}*\n\n"
        f"Share this code with your operators so they can join.\n"
        f"They should text: join {business.code} TheirName"
    )

def record_sale(db: Session, phone: str, data: dict, operator_id=None) -> str:
    role, business, op_id = get_user_context(db, phone)
    if not business:
        return "❌ Not registered. Send your business name to get started."

    customer_name = (data.get("customer") or "").strip()
    # customer_name = data.get("customer", "").strip()
    is_credit = data.get("is_credit", False)
    amount = float(data.get("amount", 0))
    item = data.get("item", "item")

    if not amount:
        return "❌ Amount not found. Please include the price."

    sale = Sale(
        business_id=business.id,
        operator_id=op_id,
        item=item,
        amount=amount,
        customer=customer_name,
        is_credit=1 if is_credit else 0
    )
    db.add(sale)

    if customer_name and is_credit:
        customer = db.query(Customer).filter(
            Customer.business_id == business.id,
            Customer.name.ilike(f"%{customer_name}%")
        ).first()
        if not customer:
            customer = Customer(business_id=business.id, name=customer_name, balance=amount)
            db.add(customer)
        else:
            customer.balance += amount

    db.commit()

    if is_credit:
        return f"✅ {customer_name} amenunua {item} kwa mkopo - KES {amount:,.0f}"
    return f"✅ Mauzo yamerekodiwa!\n{item}: KES {amount:,.0f}" + (f"\nMteja: {customer_name}" if customer_name else "")

def record_expense(db: Session, phone: str, data: dict) -> str:
    role, business, op_id = get_user_context(db, phone)
    if not business:
        return "❌ Not registered."
    amount = float(data.get("amount", 0))
    description = data.get("description", "expense")
    if not amount:
        return "❌ Amount not found."
    expense = Expense(business_id=business.id, description=description, amount=amount)
    db.add(expense)
    db.commit()
    return f"✅ Gharama imerekodiwa!\n{description}: KES {amount:,.0f}"

def get_summary(db: Session, phone: str, period: str = "today", operator_name: str = None) -> str:
    role, business, op_id = get_user_context(db, phone)
    if not business:
        return "❌ Not registered."

    now = datetime.utcnow()
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0)
        label = "Leo"
    elif period == "week":
        start = now - timedelta(days=7)
        label = "Wiki hii"
    else:
        start = now.replace(day=1, hour=0, minute=0, second=0)
        label = "Mwezi huu"

    # operator sees only their sales
    if role == "operator":
        sales_q = db.query(Sale).filter(
            Sale.business_id == business.id,
            Sale.operator_id == op_id,
            Sale.created_at >= start
        ).all()
        label += f" (your sales)"
    # owner filtering by operator name
    elif operator_name:
        op = db.query(Operator).filter(
            Operator.business_id == business.id,
            Operator.name.ilike(f"%{operator_name}%")
        ).first()
        if not op:
            return f"❌ Operator '{operator_name}' not found."
        sales_q = db.query(Sale).filter(
            Sale.business_id == business.id,
            Sale.operator_id == op.id,
            Sale.created_at >= start
        ).all()
        label += f" ({op.name})"
    else:
        sales_q = db.query(Sale).filter(
            Sale.business_id == business.id,
            Sale.created_at >= start
        ).all()

    expenses = db.query(Expense).filter(
        Expense.business_id == business.id,
        Expense.created_at >= start
    ).all()

    total_sales = sum(s.amount for s in sales_q)
    total_expenses = sum(e.amount for e in expenses)
    profit = total_sales - total_expenses
    credit_sales = sum(s.amount for s in sales_q if s.is_credit)

    return (
        f"📊 *{label} - {business.name}:*\n\n"
        f"💰 Mauzo: KES {total_sales:,.0f}\n"
        f"📦 Gharama: KES {total_expenses:,.0f}\n"
        f"✨ Faida: KES {profit:,.0f}\n"
        f"📝 Mkopo: KES {credit_sales:,.0f}\n\n"
        f"Transactions: {len(sales_q)} sales"
    )

def get_operators_summary(db: Session, phone: str, period: str = "today") -> str:
    role, business, op_id = get_user_context(db, phone)
    if role != "owner":
        return "❌ Only the owner can see operator summaries."

    now = datetime.utcnow()
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0)
        label = "Leo"
    elif period == "week":
        start = now - timedelta(days=7)
        label = "Wiki hii"
    else:
        start = now.replace(day=1, hour=0, minute=0, second=0)
        label = "Mwezi huu"

    operators = db.query(Operator).filter(Operator.business_id == business.id).all()
    if not operators:
        return "No operators have joined yet.\nShare your business code with your staff."

    lines = [f"👥 *{label} - Per Operator:*\n"]
    for op in operators:
        sales = db.query(Sale).filter(
            Sale.business_id == business.id,
            Sale.operator_id == op.id,
            Sale.created_at >= start
        ).all()
        total = sum(s.amount for s in sales)
        lines.append(f"• {op.name}: KES {total:,.0f} ({len(sales)} sales)")

    # owner's own sales
    owner_sales = db.query(Sale).filter(
        Sale.business_id == business.id,
        Sale.operator_id == None,
        Sale.created_at >= start
    ).all()
    if owner_sales:
        total = sum(s.amount for s in owner_sales)
        lines.append(f"• You (owner): KES {total:,.0f} ({len(owner_sales)} sales)")

    return "\n".join(lines)

def check_debts(db: Session, phone: str) -> str:
    role, business, op_id = get_user_context(db, phone)
    if not business:
        return "❌ Not registered."
    customers = db.query(Customer).filter(
        Customer.business_id == business.id,
        Customer.balance > 0
    ).order_by(Customer.balance.desc()).all()
    if not customers:
        return "✅ Hakuna deni! Wote wamelipa."
    total = sum(c.balance for c in customers)
    lines = [f"📋 *Wanaokudai - KES {total:,.0f} total:*\n"]
    for c in customers:
        lines.append(f"• {c.name}: KES {c.balance:,.0f}")
    return "\n".join(lines)

def add_stock(db: Session, phone: str, data: dict) -> str:
    role, business, op_id = get_user_context(db, phone)
    if not business:
        return "❌ Not registered."
    item = data.get("item", "").strip().lower()
    quantity = float(data.get("quantity", 0))
    unit = data.get("unit", "units")
    if not item or not quantity:
        return "❌ Please specify item and quantity. E.g: stock unga 50kg"
    inv = db.query(Inventory).filter(
        Inventory.business_id == business.id,
        Inventory.item.ilike(f"%{item}%")
    ).first()
    if inv:
        inv.quantity += quantity
        inv.updated_at = datetime.utcnow()
    else:
        inv = Inventory(business_id=business.id, item=item, quantity=quantity, unit=unit)
        db.add(inv)
    db.commit()
    return f"✅ Stock updated!\n{item.title()}: {inv.quantity:g} {unit}"

def check_stock(db: Session, phone: str) -> str:
    role, business, op_id = get_user_context(db, phone)
    if not business:
        return "❌ Not registered."
    items = db.query(Inventory).filter(
        Inventory.business_id == business.id
    ).order_by(Inventory.item).all()
    if not items:
        return "📦 No stock recorded yet.\nType 'stock unga 50kg' to add stock."
    lines = ["📦 *Current Stock:*\n"]
    for i in items:
        warning = " ⚠️ LOW" if i.quantity <= i.min_level else ""
        lines.append(f"• {i.item.title()}: {i.quantity:g} {i.unit}{warning}")
    return "\n".join(lines)

def low_stock(db: Session, phone: str) -> str:
    role, business, op_id = get_user_context(db, phone)
    if not business:
        return "❌ Not registered."
    items = db.query(Inventory).filter(
        Inventory.business_id == business.id,
        Inventory.quantity <= Inventory.min_level
    ).all()
    if not items:
        return "✅ All stock levels are okay!"
    lines = ["⚠️ *Low Stock Alert:*\n"]
    for i in items:
        lines.append(f"• {i.item.title()}: only {i.quantity:g} {i.unit} left")
    return "\n".join(lines)