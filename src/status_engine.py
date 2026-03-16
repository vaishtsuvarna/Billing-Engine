import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

SUSPENSION_THRESHOLD = 1.5


def evaluate_status(subscription: Dict, total_usage_gb: float) -> str:
    """Evaluate the final status for a subscription based on usage."""
    sub_id = subscription["subscription_id"]
    current_status = subscription["status"]
    usage_limit = subscription["usage_limit_gb"]

    if current_status == "CANCELLED":
        logger.debug(f"{sub_id}: CANCELLED — status unchanged")
        return "CANCELLED"

    if usage_limit > 0 and total_usage_gb > SUSPENSION_THRESHOLD * usage_limit:
        if current_status != "SUSPENDED":
            logger.info(f"{sub_id}: usage {total_usage_gb:.2f}GB exceeds 150% of limit {usage_limit}GB — suspending")
        return "SUSPENDED"

    if current_status == "SUSPENDED" and total_usage_gb <= usage_limit:
        logger.info(f"{sub_id}: previously SUSPENDED, usage now within limit — reactivating to ACTIVE")
        return "ACTIVE"

    return current_status


def apply_statuses(subscriptions: List[Dict], usage_totals: Dict[str, float], billing_results: List[Dict]) -> List[Dict]:
    """Attach final_status to each billing result."""
    sub_map = {s["subscription_id"]: s for s in subscriptions}

    for result in billing_results:
        sub_id = result["subscription_id"]
        sub = sub_map.get(sub_id)
        if not sub:
            logger.warning(f"{sub_id}: no subscription record found for status evaluation")
            result["final_status"] = "UNKNOWN"
            continue
        usage = usage_totals.get(sub_id, 0.0)
        result["final_status"] = evaluate_status(sub, usage)

    return billing_results