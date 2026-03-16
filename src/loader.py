import csv
import logging
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)

VALID_STATUSES = {"ACTIVE", "SUSPENDED", "CANCELLED"}
VALID_PLANS = {"Basic", "Premium", "Standard"}


def load_subscriptions(filepath: str) -> List[Dict]:
    subscriptions = []
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=2):
                sub = _parse_subscription(row, i)
                if sub:
                    subscriptions.append(sub)
    except FileNotFoundError:
        logger.error(f"Subscriptions file not found: {filepath}")
    except Exception as e:
        logger.error(f"Unexpected error reading subscriptions: {e}")
    logger.info(f"Loaded {len(subscriptions)} valid subscriptions")
    return subscriptions


def load_usage(filepath: str) -> List[Dict]:
    records = []
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=2):
                record = _parse_usage(row, i)
                if record:
                    records.append(record)
    except FileNotFoundError:
        logger.error(f"Usage file not found: {filepath}")
    except Exception as e:
        logger.error(f"Unexpected error reading usage: {e}")
    logger.info(f"Loaded {len(records)} valid usage records")
    return records


def _parse_subscription(row: Dict, line: int) -> Dict | None:
    try:
        sub_id = row.get("subscription_id", "").strip()
        if not sub_id:
            logger.warning(f"Line {line}: missing subscription_id, skipping")
            return None

        status = row.get("status", "").strip().upper()
        if status not in VALID_STATUSES:
            logger.warning(f"Line {line}: invalid status '{status}' for {sub_id}, skipping")
            return None

        plan = row.get("plan", "").strip().title()
        if plan not in VALID_PLANS:
            logger.warning(f"Line {line}: invalid plan '{plan}' for {sub_id}, skipping")
            return None

        try:
            monthly_fee = float(row.get("monthly_fee", 0))
        except (ValueError, TypeError):
            logger.warning(f"Line {line}: invalid monthly_fee for {sub_id}, defaulting to 0")
            monthly_fee = 0.0

        try:
            usage_limit = float(row.get("usage_limit_gb", 0))
        except (ValueError, TypeError):
            logger.warning(f"Line {line}: invalid usage_limit_gb for {sub_id}, defaulting to 0")
            usage_limit = 0.0

        start_date = _parse_date(row.get("start_date", ""), sub_id, line, "start_date")
        end_date_str = row.get("end_date", "").strip()
        end_date = _parse_date(end_date_str, sub_id, line, "end_date") if end_date_str else None

        return {
            "subscription_id": sub_id,
            "customer_id": row.get("customer_id", "").strip(),
            "plan": plan,
            "monthly_fee": monthly_fee,
            "usage_limit_gb": usage_limit,
            "status": status,
            "start_date": start_date,
            "end_date": end_date,
        }
    except Exception as e:
        logger.error(f"Line {line}: unexpected error parsing subscription: {e}")
        return None


def _parse_usage(row: Dict, line: int) -> Dict | None:
    try:
        sub_id = row.get("subscription_id", "").strip()
        if not sub_id:
            logger.warning(f"Line {line}: missing subscription_id in usage, skipping")
            return None

        date_str = row.get("usage_date", "").strip()
        usage_date = _parse_date(date_str, sub_id, line, "usage_date")
        if not usage_date:
            return None

        raw_gb = row.get("data_used_gb", "").strip()
        if not raw_gb:
            logger.warning(f"Line {line}: missing data_used_gb for {sub_id}, defaulting to 0")
            data_used_gb = 0.0
        else:
            try:
                data_used_gb = float(raw_gb)
            except ValueError:
                logger.warning(f"Line {line}: invalid data_used_gb '{raw_gb}' for {sub_id}, defaulting to 0")
                data_used_gb = 0.0

        return {
            "subscription_id": sub_id,
            "usage_date": usage_date,
            "data_used_gb": data_used_gb,
        }
    except Exception as e:
        logger.error(f"Line {line}: unexpected error parsing usage record: {e}")
        return None


def _parse_date(date_str: str, sub_id: str, line: int, field: str) -> datetime | None:
    if not date_str or not date_str.strip():
        return None
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d")
    except ValueError:
        logger.warning(f"Line {line}: invalid date '{date_str}' in field '{field}' for {sub_id}, skipping")
        return None