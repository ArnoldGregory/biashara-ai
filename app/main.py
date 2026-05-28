from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from database import init_db, SessionLocal
from ai import understand_message
from logic import record_sale, record_expense, get_summary, check_debts
from logic import record_sale, record_expense, get_summary, check_debts, add_stock, check_stock, low_stock

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
        result = understand_message(message)
        intent = result.get("intent", "unknown")
        data = result.get("data", {})

        if intent == "record_sale":
            reply = record_sale(db, phone, data)
        elif intent == "record_expense":
            reply = record_expense(db, phone, data)
        elif intent == "get_summary":
            reply = get_summary(db, phone, data.get("period", "today"))
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
                "Habari! Biashara AI 🤖\n\n"
                "• Sale: 'unga 200' or 'sugar 480'\n"
                "• Credit: 'milk 50 mkopo John'\n"
                "• Expense: 'expense transport 300'\n"
                "• Summary: 'today' or 'week'\n"
                "• Debts: 'debts'"
            )

        return JSONResponse({"phone": phone, "reply": reply})
    finally:
        db.close()