import csv
import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

OUTPUT_COLUMNS = [
    "subscription_id", "customer_id", "plan",
    "total_usage_gb", "overage_gb", "total_bill", "final_status"
]


def write_billing_output(results: List[Dict], filepath: str) -> None:
    try:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(results)
        logger.info(f"Billing output written to {filepath}")
    except Exception as e:
        logger.error(f"Failed to write billing output: {e}")


def write_billing_summary(results: List[Dict], filepath: str) -> None:
    try:
        status_counts = {"ACTIVE": 0, "SUSPENDED": 0, "CANCELLED": 0}
        total_revenue = 0.0

        for r in results:
            status = r.get("final_status", "UNKNOWN")
            if status in status_counts:
                status_counts[status] += 1
            total_revenue += r.get("total_bill", 0.0)

        non_cancelled = [r for r in results if r.get("final_status") != "CANCELLED"]
        avg_bill = round(total_revenue / len(non_cancelled), 2) if non_cancelled else 0.0

        summary = {
            "total_subscriptions": len(results),
            "active_subscriptions": status_counts["ACTIVE"],
            "suspended_subscriptions": status_counts["SUSPENDED"],
            "cancelled_subscriptions": status_counts["CANCELLED"],
            "total_revenue": round(total_revenue, 2),
            "average_bill": avg_bill,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Billing summary written to {filepath}")
    except Exception as e:
        logger.error(f"Failed to write billing summary: {e}")