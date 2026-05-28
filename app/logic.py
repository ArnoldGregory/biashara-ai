from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import Business, Sale, Expense, Customer, get_or_create_business

def record_sale(db: Session, phone: str, data: dict) -> str:
    business = get_or_create_business(db, phone)
    customer_name = data.get("customer", "").strip()
    is_credit = data.get("is_credit", False)
    amount = float(data.get("amount", 0))
    item = data.get("item", "item")

    if not amount:
        return "❌ Sikupata amount. Sema tena na bei."

    sale = Sale(
        business_id=business.id,
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
            customer = Customer(
                business_id=business.id,
                name=customer_name,
                balance=amount
            )
            db.add(customer)
        else:
            customer.balance += amount

    db.commit()

    if is_credit:
        return f"✅ {customer_name} amenunua {item} kwa mkopo - KES {amount:,.0f}"
    return f"✅ Mauzo yamerekodiwa!\n{item}: KES {amount:,.0f}" + (f"\nMteja: {customer_name}" if customer_name else "")

def record_expense(db: Session, phone: str, data: dict) -> str:
    business = get_or_create_business(db, phone)
    amount = float(data.get("amount", 0))
    description = data.get("description", "expense")

    if not amount:
        return "❌ Sikupata amount. Sema tena na bei."

    expense = Expense(business_id=business.id, description=description, amount=amount)
    db.add(expense)
    db.commit()
    return f"✅ Gharama imerekodiwa!\n{description}: KES {amount:,.0f}"

def get_summary(db: Session, phone: str, period: str = "today") -> str:
    business = get_or_create_business(db, phone)
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

    sales = db.query(Sale).filter(Sale.business_id == business.id, Sale.created_at >= start).all()
    expenses = db.query(Expense).filter(Expense.business_id == business.id, Expense.created_at >= start).all()

    total_sales = sum(s.amount for s in sales)
    total_expenses = sum(e.amount for e in expenses)
    profit = total_sales - total_expenses
    credit_sales = sum(s.amount for s in sales if s.is_credit)

    return (
        f"📊 *{label} - Biashara Yako:*\n\n"
        f"💰 Mauzo: KES {total_sales:,.0f}\n"
        f"📦 Gharama: KES {total_expenses:,.0f}\n"
        f"✨ Faida: KES {profit:,.0f}\n"
        f"📝 Mkopo: KES {credit_sales:,.0f}\n\n"
        f"Transactions: {len(sales)} sales, {len(expenses)} expenses"
    )

def check_debts(db: Session, phone: str) -> str:
    business = get_or_create_business(db, phone)
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