import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from datetime import datetime
from usage_aggregator import aggregate_usage

def make_record(sub_id, date_str, gb):
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        date = None
    return {"subscription_id": sub_id, "usage_date": date, "data_used_gb": gb}


class TestUsageAggregator(unittest.TestCase):

    def test_multiple_usage_records(self):
        """Multiple valid March records for same sub are summed correctly."""
        records = [
            make_record("SUB001", "2024-03-01", 10.0),
            make_record("SUB001", "2024-03-15", 20.0),
            make_record("SUB001", "2024-03-28", 15.5),
        ]
        result = aggregate_usage(records)
        self.assertAlmostEqual(result["SUB001"], 45.5, places=2)

    def test_no_usage_records(self):
        """Subscription with no usage records returns 0 (missing key, not error)."""
        records = [make_record("SUB002", "2024-03-10", 5.0)]
        result = aggregate_usage(records)
        self.assertEqual(result.get("SUB999", 0.0), 0.0)

    def test_invalid_usage_dates(self):
        """Records with invalid/None dates are skipped entirely."""
        records = [
            {"subscription_id": "SUB003", "usage_date": None, "data_used_gb": 50.0},
            make_record("SUB003", "2024-03-10", 20.0),
        ]
        result = aggregate_usage(records)
        self.assertAlmostEqual(result.get("SUB003", 0.0), 20.0, places=2)

    def test_other_month_records_excluded(self):
        """Records from months other than March 2024 are excluded."""
        records = [
            make_record("SUB004", "2024-02-15", 100.0),  # February — excluded
            make_record("SUB004", "2024-01-10", 200.0),  # January — excluded
            make_record("SUB004", "2024-03-05", 30.0),   # March — included
        ]
        result = aggregate_usage(records)
        self.assertAlmostEqual(result["SUB004"], 30.0, places=2)

    def test_multiple_subscriptions_aggregated_independently(self):
        """Usage for different subs does not bleed into each other."""
        records = [
            make_record("SUB005", "2024-03-01", 50.0),
            make_record("SUB006", "2024-03-01", 75.0),
            make_record("SUB005", "2024-03-20", 25.0),
        ]
        result = aggregate_usage(records)
        self.assertAlmostEqual(result["SUB005"], 75.0, places=2)
        self.assertAlmostEqual(result["SUB006"], 75.0, places=2)

    def test_empty_records_returns_empty_dict(self):
        """Empty input returns empty dict without errors."""
        result = aggregate_usage([])
        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()