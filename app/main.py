from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from database import init_db, SessionLocal, get_user_context
from ai import understand_message
from logic import (record_sale, record_expense, get_summary,
                   check_debts, add_stock, check_stock, low_stock,
                   handle_new_user, get_operators_summary)

load_dotenv()
app = FastAPI(title="Biashara AI")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.post("/message")
async def handle_message(phone: str = Form(...), message: str = Form(...)):
    db = SessionLocal()
    try:
        role, business, op_id = get_user_context(db, phone)

        # new user flow
        if role == "new":
            if message.strip().lower().startswith("join "):
                reply = handle_new_user(db, phone, message)
            else:
                reply = (
                    "👋 Welcome to *Biashara AI!*\n\n"
                    "What is the name of your business?\n"
                    "Example: *Mama Stacy Shop*\n\n"
                    "Or if you're joining an existing business:\n"
                    "*join BUSINESSCODE YourName*"
                )
                # if they typed a business name directly
                if len(message.strip()) > 3 and not message.strip().lower().startswith("join"):
                    reply = handle_new_user(db, phone, message)
            return JSONResponse({"phone": phone, "reply": reply})

        # existing user
        result = understand_message(message)
        intent = result.get("intent", "unknown")
        data = result.get("data", {})

        if intent == "record_sale":
            reply = record_sale(db, phone, data)
        elif intent == "record_expense":
            reply = record_expense(db, phone, data)
        elif intent == "get_summary":
            reply = get_summary(db, phone, data.get("period", "today"), data.get("operator_name"))
        elif intent == "get_operators_summary":
            reply = get_operators_summary(db, phone, data.get("period", "today"))
        elif intent == "check_debts":
            reply = check_debts(db, phone)
        elif intent == "add_stock":
            reply = add_stock(db, phone, data)
        elif intent == "check_stock":
            reply = check_stock(db, phone)
        elif intent == "low_stock":
            reply = low_stock(db, phone)
        else:
            reply = (
                "Biashara AI 🤖\n\n"
                "• Sale: 'unga 200' or 'sugar 480'\n"
                "• Credit: 'milk 50 mkopo John'\n"
                "• Expense: 'expense transport 300'\n"
                "• Stock: 'stock unga 50kg'\n"
                "• Summary: 'today' or 'week'\n"
                "• Staff: 'operators today'\n"
                "• Debts: 'debts'"
            )

        return JSONResponse({"phone": phone, "reply": reply})
    finally:
        db.close()