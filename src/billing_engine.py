import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

OVERAGE_RATE_PER_GB = 10.0


def calculate_bill(subscription: Dict, total_usage_gb: float) -> Dict:
    """Calculate billing fields for a single subscription."""
    sub_id = subscription["subscription_id"]
    status = subscription["status"]
    monthly_fee = subscription["monthly_fee"]
    usage_limit = subscription["usage_limit_gb"]

    if status == "CANCELLED":
        logger.debug(f"{sub_id}: CANCELLED — bill = 0")
        return {
            "subscription_id": sub_id,
            "customer_id": subscription["customer_id"],
            "plan": subscription["plan"],
            "total_usage_gb": round(total_usage_gb, 4),
            "overage_gb": 0.0,
            "total_bill": 0.0,
        }

    overage_gb = max(0.0, total_usage_gb - usage_limit)

    if status == "SUSPENDED":
        total_bill = monthly_fee
        overage_gb = 0.0
        logger.debug(f"{sub_id}: SUSPENDED — bill = monthly_fee only ({monthly_fee})")
    elif total_usage_gb <= usage_limit:
        total_bill = monthly_fee
        logger.debug(f"{sub_id}: no overage — bill = {monthly_fee}")
    else:
        overage_charge = overage_gb * OVERAGE_RATE_PER_GB
        total_bill = monthly_fee + overage_charge
        logger.debug(f"{sub_id}: overage {overage_gb:.2f}GB — bill = {total_bill:.2f}")

    return {
        "subscription_id": sub_id,
        "customer_id": subscription["customer_id"],
        "plan": subscription["plan"],
        "total_usage_gb": round(total_usage_gb, 4),
        "overage_gb": round(overage_gb, 4),
        "total_bill": round(total_bill, 2),
    }


def process_all_billing(subscriptions: List[Dict], usage_totals: Dict[str, float]) -> List[Dict]:
    """Run billing for all subscriptions."""
    results = []
    for sub in subscriptions:
        sub_id = sub["subscription_id"]
        usage = usage_totals.get(sub_id, 0.0)
        result = calculate_bill(sub, usage)
        results.append(result)
    logger.info(f"Billing calculated for {len(results)} subscriptions")
    return results