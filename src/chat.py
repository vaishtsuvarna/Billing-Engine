import os
import csv
import json
import sys

try:
    from groq import Groq
except ImportError:
    print("Missing package. Run:  pip install groq python-dotenv")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

#paths
BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BILLING_OUTPUT  = os.path.join(BASE_DIR, "outputs", "billing_output.csv")
BILLING_SUMMARY = os.path.join(BASE_DIR, "outputs", "billing_summary.json")

#terminal colours
ORANGE = "\033[38;5;214m"
CYAN   = "\033[96m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


def load_billing_data() -> str:
    lines = []

    try:
        with open(BILLING_SUMMARY, "r") as f:
            summary = json.load(f)
        lines.append("=== BILLING SUMMARY ===")
        for k, v in summary.items():
            lines.append(f"  {k}: {v}")
        lines.append("")
    except FileNotFoundError:
        lines.append("(billing_summary.json not found — run main.py first)")

    try:
        with open(BILLING_OUTPUT, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        lines.append("=== FULL BILLING RECORDS ===")
        lines.append(
            f"{'subscription_id':<15} {'customer_id':<12} {'plan':<12} "
            f"{'usage_gb':<12} {'overage_gb':<12} {'total_bill':<12} {'status'}"
        )
        lines.append("-" * 85)
        for r in rows:
            lines.append(
                f"{r['subscription_id']:<15} {r['customer_id']:<12} {r['plan']:<12} "
                f"{r['total_usage_gb']:<12} {r['overage_gb']:<12} "
                f"${float(r['total_bill']):<11.2f} {r['final_status']}"
            )
    except FileNotFoundError:
        lines.append("(billing_output.csv not found — run main.py first)")

    return "\n".join(lines)


def build_system_prompt(billing_data: str) -> str:
    return f"""You are a billing analytics assistant for a subscription-based digital service.
You have access to the company's complete billing data shown below.
Answer user questions clearly and concisely based on this data.
When making recommendations, be specific — mention actual subscription IDs and numbers.
If a question cannot be answered from the data, say so honestly.

Business rules:
- Plans: Basic, Standard, Premium
- Overage charged at $10 per GB over the limit
- Status: ACTIVE, SUSPENDED, or CANCELLED
- Subscriptions using >150% of their limit get SUSPENDED
- SUSPENDED subscriptions are billed at base monthly fee only (no overage)

{billing_data}
"""


def chat():
    #API key check
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print(f"\n{YELLOW}No GROQ_API_KEY found.{RESET}")
        print("Steps:")
        print("  1. Go to https://console.groq.com and sign up (free)")
        print("  2. Create an API key")
        print("  3. Add to your .env file:  GROQ_API_KEY=your_key_here")
        print("  4. Run again\n")
        sys.exit(1)

    # load data 
    print(f"\n{CYAN}Loading billing data...{RESET}", end=" ")
    billing_data = load_billing_data()
    system_prompt = build_system_prompt(billing_data)
    print(f"{ORANGE}done.{RESET}")

    #setup Groq
    client = Groq(api_key=api_key)
    conversation_history = []

    # opening 
    print(f"""
{BOLD}{ORANGE}╔══════════════════════════════════════════════════╗
║       Billing Analytics AI Assistant             ║
║       Powered by Groq — Llama 3                  ║
╚══════════════════════════════════════════════════╝{RESET}

{CYAN}Example queries:{RESET}
  • Which subscriptions have the highest overage charges?
  • Who is at risk of suspension?
  • Which customers should be prioritised for collections?

Type {RED}'exit'{RESET} or {RED}'quit'{RESET} to stop.
Type {RED}'data'{RESET} to see the raw billing data being used.
Type {RED}'clear'{RESET} to reset conversation history.
{'-' * 52}""")

    # main chat loop
    while True:
        try:
            user_input = input(f"\n{BOLD}You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{CYAN}Goodbye!{RESET}")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print(f"\n{RED}Goodbye!{RESET}")
            break

        if user_input.lower() == "data":
            print(f"\n{CYAN}{billing_data}{RESET}")
            continue

        if user_input.lower() == "clear":
            conversation_history = []
            print(f"\n{ORANGE}Conversation history cleared.{RESET}")
            continue

        conversation_history.append({
            "role": "user",
            "content": user_input
        })

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *conversation_history
                ],
                temperature=0.7,
                max_tokens=1024,
            )

            reply = response.choices[0].message.content

            conversation_history.append({
                "role": "assistant",
                "content": reply
            })

            print(f"\n{ORANGE}Assistant:{RESET} {CYAN}{reply}{RESET}")

        except Exception as e:
            err = str(e)
            if "429" in err or "rate" in err.lower():
                print(f"{YELLOW}Rate limit hit — wait a moment and try again.{RESET}")
            elif "401" in err or "api_key" in err.lower() or "auth" in err.lower():
                print(f"{YELLOW}Invalid API key — check your GROQ_API_KEY in .env{RESET}")
            else:
                print(f"{YELLOW}Error: {e}{RESET}")
            if conversation_history and conversation_history[-1]["role"] == "user":
                conversation_history.pop()


if __name__ == "__main__":
    chat()