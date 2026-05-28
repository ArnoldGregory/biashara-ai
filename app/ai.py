from dotenv import load_dotenv
load_dotenv()

import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
SYSTEM_PROMPT = """
You are Biashara AI, a business assistant for small Kenyan businesses.
You understand English, Swahili, and Sheng mixed together.

Always respond with ONLY a JSON object, nothing else. No explanation, no markdown.

{
  "intent": "record_sale | record_expense | get_summary | check_debts | send_reminder | add_stock | check_stock | low_stock | unknown",
  "data": {
    "item": "item name",
    "amount": 0,
    "customer": "customer name if mentioned",
    "is_credit": false,
    "description": "description if expense",
    "period": "today | week | month",
    "customer_to_remind": "name if sending reminder",
    "quantity": 0,
    "unit": "kg | litres | packets | units"
  },
  "reply": "friendly confirmation in English, one line max"
}

Sale examples:
- "unga 200" → record_sale, item=unga, amount=200
- "sugar 480 mkopo Kamau" → record_sale, item=sugar, amount=480, customer=Kamau, is_credit=true
- "unga 500 sugar 480" → record_sale, item=unga+sugar, amount=980

Expense examples:
- "expense transport 500" → record_expense
- "spent 3000 stock" → record_expense, amount=3000, description=stock

Stock examples:
- "stock unga 50kg" → add_stock, item=unga, quantity=50, unit=kg
- "stock sugar 20 packets" → add_stock, item=sugar, quantity=20, unit=packets
- "stock check" or "stock" → check_stock
- "low stock" or "what is finishing" → low_stock

Summary examples:
- "today" or "leo" → get_summary, period=today
- "week" or "wiki" → get_summary, period=week
- "month" or "mwezi" → get_summary, period=month

Debt examples:
- "debts" or "who owes" → check_debts

Keep replies SHORT — one line max.
"""

def understand_message(message: str) -> dict:
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            temperature=0.1,
            max_tokens=300
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        print(f"AI error: {e}")
        return {
            "intent": "unknown",
            "data": {},
            "reply": "Samahani, sijuelewa. Jaribu tena."
        }