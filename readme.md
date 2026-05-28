# Biashara AI 🏪
 
> AI-powered business assistant for Kenyan SMEs — record sales, track expenses, and manage debts in plain English or Swahili.
 
![Biashara AI](https://img.shields.io/badge/Status-Live-brightgreen) ![Python](https://img.shields.io/badge/Python-3.10-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-latest-green) ![Groq](https://img.shields.io/badge/LLM-Groq%20LLaMA3-orange)
 
---
 
## What is Biashara AI?
 
Biashara AI is a conversational business management tool built for small Kenyan businesses — mama mbogas, dukas, salons, hardware shops. Instead of complex software, business owners simply type or speak naturally and the AI handles the rest.
 
No app to download. No training needed. Just type like you're texting.
 
---
 
## Features
 
- **Record sales** in short form — `unga 200 sugar 480`
- **Credit sales** — `milk 50 mkopo John`
- **Track expenses** — `expense transport 300`
- **Daily/weekly/monthly summaries** — `today`, `week`, `month`
- **Debt tracking** — `debts` shows everyone who owes you
- **Swahili + English + Sheng** — the AI understands all three
- **Voice notes** — coming in Phase 2 via OpenAI Whisper
---
 
## Tech Stack
 
| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| AI Understanding | Groq LLaMA 3.3 70B |
| Database | SQLite via SQLAlchemy |
| Frontend | Vanilla HTML/CSS/JS |
| WhatsApp (coming) | Africa's Talking / Meta Cloud API |
 
---
 
## Getting Started
 
### 1. Clone the repo
```bash
git clone https://github.com/ArnoldGregory/biashara-ai.git
cd biashara-ai
```
 
### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```
 
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
 
### 4. Set up environment variables
```bash
cp .env.example .env
# Add your GROQ_API_KEY from console.groq.com (free)
```
 
### 5. Run the server
```bash
cd app
uvicorn main:app --reload --port 8000
```
 
### 6. Open the UI
```
http://localhost:8000
```
 
---
 
## Usage Examples
 
```
unga 500                          → records sale of unga for KES 500
sugar 480 milk 60                 → records multiple items, total KES 540
bread 60 mkopo John               → credit sale, John owes KES 60
expense transport 300             → records expense
today                             → summary of today's sales and profit
week                              → this week's report
debts                             → lists all customers who owe money
Niliuza sukari kwa 150 kwa Mary   → Swahili works too
```
 
---
 
## Roadmap
 
- [x] Core sale and expense recording
- [x] Debt tracking
- [x] Natural language understanding (English + Swahili)
- [x] Web chat UI
- [ ] Voice note support via Whisper
- [ ] WhatsApp integration via Meta Cloud API
- [ ] M-Pesa STK push for payments
- [ ] Daily automated summary at 9pm
- [ ] Multi-business support
---
 
## Why Biashara AI?
 
Kenya has 7.4 million SMEs. Most track their business on paper or in their head. Existing solutions like Odoo are too complex and too expensive. Biashara AI meets business owners where they already are — on WhatsApp — and speaks their language.
 
---
 
## Author
 
**Arnold Omondi** — Backend & AI Engineer, Nairobi Kenya  
[LinkedIn](https://linkedin.com/in/arnold-omondi) · [GitHub](https://github.com/ArnoldGregory)