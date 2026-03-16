import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loader import load_subscriptions, load_usage
from usage_aggregator import aggregate_usage
from billing_engine import process_all_billing
from status_engine import apply_statuses
from reporter import write_billing_output, write_billing_summary


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SUBSCRIPTIONS_FILE = os.path.join(BASE_DIR, "data", "subscriptions.csv")
USAGE_FILE = os.path.join(BASE_DIR, "data", "usage.csv")
BILLING_OUTPUT = os.path.join(BASE_DIR, "outputs", "billing_output.csv")
BILLING_SUMMARY = os.path.join(BASE_DIR, "outputs", "billing_summary.json")
DASHBOARD_FILE = os.path.join(BASE_DIR, "outputs", "dashboard.html")
LOG_FILE = os.path.join(BASE_DIR, "logs", "billing.log")


def setup_logging():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE)
        ],
    )


def main():
    setup_logging()
    logger = logging.getLogger("main")
    logger.info("=== Billing Engine Started ===")

    os.makedirs(os.path.dirname(BILLING_OUTPUT), exist_ok=True)

    logger.info("Loading data...")
    subscriptions = load_subscriptions(SUBSCRIPTIONS_FILE)
    usage_records = load_usage(USAGE_FILE)

    if not subscriptions:
        logger.error("No valid subscriptions loaded. Exiting.")
        return

    logger.info("Aggregating usage...")
    usage_totals = aggregate_usage(usage_records)

    logger.info("Calculating bills...")
    billing_results = process_all_billing(subscriptions, usage_totals)

    logger.info("Evaluating statuses...")
    billing_results = apply_statuses(subscriptions, usage_totals, billing_results)

    logger.info("Writing outputs...")
    write_billing_output(billing_results, BILLING_OUTPUT)
    write_billing_summary(billing_results, BILLING_SUMMARY)
    

    logger.info("=== Billing Engine Completed Successfully ===")
    print(f"\n  Outputs written to:")
    print(f"    {BILLING_OUTPUT}")
    print(f"    {BILLING_SUMMARY}")
    


if __name__ == "__main__":
    main()