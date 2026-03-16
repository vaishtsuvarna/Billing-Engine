import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from billing_engine import calculate_bill, process_all_billing

BASE_SUB = {
    "subscription_id": "SUB_TEST",
    "customer_id": "CUST_TEST",
    "plan": "Pro",
    "monthly_fee": 59.99,
    "usage_limit_gb": 150.0,
    "status": "ACTIVE",
}

class TestBillingEngine(unittest.TestCase):

    def test_bill_without_overage(self):
        """Usage within limit: bill equals monthly_fee only."""
        result = calculate_bill({**BASE_SUB}, 100.0)
        self.assertEqual(result["total_bill"], 59.99)
        self.assertEqual(result["overage_gb"], 0.0)

    def test_bill_with_overage(self):
        """Usage exceeds limit: bill = monthly_fee + overage_gb * 10."""
        result = calculate_bill({**BASE_SUB}, 200.0)
        expected_overage = 200.0 - 150.0  # 50 GB
        expected_bill = 59.99 + (expected_overage * 10)  # 59.99 + 500 = 559.99
        self.assertAlmostEqual(result["total_bill"], expected_bill, places=2)
        self.assertAlmostEqual(result["overage_gb"], expected_overage, places=2)

    def test_suspended_subscription_billing(self):
        """SUSPENDED subscriptions billed at monthly_fee only, no overage."""
        sub = {**BASE_SUB, "status": "SUSPENDED"}
        result = calculate_bill(sub, 300.0)  # way over limit
        self.assertEqual(result["total_bill"], 59.99)
        self.assertEqual(result["overage_gb"], 0.0)

    def test_cancelled_subscription_billing(self):
        """CANCELLED subscriptions are billed $0."""
        sub = {**BASE_SUB, "status": "CANCELLED"}
        result = calculate_bill(sub, 500.0)
        self.assertEqual(result["total_bill"], 0.0)
        self.assertEqual(result["overage_gb"], 0.0)

    def test_usage_exactly_at_limit(self):
        """Usage exactly at limit: no overage charged."""
        result = calculate_bill({**BASE_SUB}, 150.0)
        self.assertEqual(result["total_bill"], 59.99)
        self.assertEqual(result["overage_gb"], 0.0)

    def test_zero_usage(self):
        """Zero usage still charges monthly_fee."""
        result = calculate_bill({**BASE_SUB}, 0.0)
        self.assertEqual(result["total_bill"], 59.99)

    def test_process_all_billing_returns_correct_count(self):
        """process_all_billing returns one result per subscription."""
        subs = [{**BASE_SUB, "subscription_id": f"SUB00{i}"} for i in range(5)]
        usage_totals = {f"SUB00{i}": i * 30.0 for i in range(5)}
        results = process_all_billing(subs, usage_totals)
        self.assertEqual(len(results), 5)


if __name__ == "__main__":
    unittest.main()