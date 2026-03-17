import logging
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

BILLING_YEAR = 2024
BILLING_MONTH = 3


def aggregate_usage(usage_records: List[Dict]) -> Dict[str, float]:
    """Aggregate total data usage per subscription for the billing month."""
    totals: Dict[str, float] = {}

    for record in usage_records:
        usage_date = record.get("usage_date")
        if not isinstance(usage_date, datetime):
            logger.warning(f"Skipping record with invalid date type: {record}")
            continue

        if usage_date.year != BILLING_YEAR or usage_date.month != BILLING_MONTH:
            continue

        sub_id = record["subscription_id"]
        gb = record.get("data_used_gb", 0.0)
        totals[sub_id] = round(totals.get(sub_id, 0.0) + gb, 4)

    logger.info(f"Aggregated usage for {len(totals)} subscriptions in {BILLING_YEAR}-{BILLING_MONTH:02d}")
    return totals