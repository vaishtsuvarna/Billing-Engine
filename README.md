# Billing-Engine

A modular Python billing pipeline that processes subscription and usage data and applies billing business rules.
 
---
 
## Project Structure
 
```
billing_project/
├── data/
│   ├── subscriptions.csv
│   └── usage.csv
├── src/
│   ├── loader.py
│   ├── usage_aggregator.py
│   ├── billing_engine.py
│   ├── status_engine.py
│   ├── reporter.py
│   ├── chat.py
│   └── main.py
├── tests/
│   ├── test_billing_engine.py
│   ├── test_status_engine.py
│   └── test_usage_aggregator.py
├── logs/
│   └── billing.log
├── outputs/
│   ├── billing_output.csv
│   └── billing_summary.json
└── .env
```
 
---
 
## How to Run
 
```bash
python src/main.py
```
 
---
 
## How to Run Tests
 
```bash
python -m pytest tests/ -v
```
 
---
 
## AI Chatbot (Extra Feature)
 
Add your Groq API key to `.env`:
```
GROQ_API_KEY=your_key_here
```
Get a free key at [console.groq.com](https://console.groq.com), then run:
```bash
python src/chat.py
```
 
---
 
## Business Rules
 
| Scenario | Bill |
|----------|------|
| Usage ≤ limit | `monthly_fee` |
| Usage > limit | `monthly_fee + (overage_gb × $10)` |
| SUSPENDED | `monthly_fee` only |
| CANCELLED | `$0` |
 
---
 
## Assumptions
 
- Only March 2024 usage records are billed
- Invalid rows are skipped and logged
- Plan names in CSV are case-insensitive
- Overage rate is $10/GB
