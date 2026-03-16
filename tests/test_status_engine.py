import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from status_engine import evaluate_status, apply_statuses

BASE_SUB = {
    "subscription_id": "SUB_TEST",
    "usage_limit_gb": 100.0,
    "status": "ACTIVE",
}

class TestStatusEngine(unittest.TestCase):

    def test_active_to_suspended_transition(self):
        """Usage > 150% of limit triggers SUSPENDED."""
        sub = {**BASE_SUB, "status": "ACTIVE"}
        result = evaluate_status(sub, 155.0)  # 155% of 100
        self.assertEqual(result, "SUSPENDED")

    def test_suspended_to_active_transition(self):
        """Previously SUSPENDED with usage <= limit reactivates to ACTIVE."""
        sub = {**BASE_SUB, "status": "SUSPENDED"}
        result = evaluate_status(sub, 80.0)  # within limit
        self.assertEqual(result, "ACTIVE")

    def test_cancelled_status_unchanged(self):
        """CANCELLED status never changes regardless of usage."""
        sub = {**BASE_SUB, "status": "CANCELLED"}
        result = evaluate_status(sub, 999.0)
        self.assertEqual(result, "CANCELLED")

    def test_active_stays_active_within_limit(self):
        """ACTIVE subscription with usage under 150% stays ACTIVE."""
        sub = {**BASE_SUB, "status": "ACTIVE"}
        result = evaluate_status(sub, 140.0)  # 140% — under threshold
        self.assertEqual(result, "ACTIVE")

    def test_suspended_stays_suspended_above_limit(self):
        """SUSPENDED subscription with usage still above limit stays SUSPENDED."""
        sub = {**BASE_SUB, "status": "SUSPENDED"}
        result = evaluate_status(sub, 120.0)  # over limit, stays suspended
        self.assertEqual(result, "SUSPENDED")

    def test_exactly_at_suspension_threshold(self):
        """Usage at exactly 150% stays ACTIVE (threshold is strictly greater than)."""
        sub = {**BASE_SUB, "status": "ACTIVE"}
        result = evaluate_status(sub, 150.0)  # exactly 150% — not over
        self.assertEqual(result, "ACTIVE")

    def test_apply_statuses_attaches_final_status(self):
        """apply_statuses correctly attaches final_status to billing results."""
        subs = [{**BASE_SUB, "subscription_id": "SUB001", "status": "ACTIVE", "usage_limit_gb": 100.0}]
        usage_totals = {"SUB001": 200.0}  # 200% — should suspend
        billing_results = [{"subscription_id": "SUB001"}]
        result = apply_statuses(subs, usage_totals, billing_results)
        self.assertEqual(result[0]["final_status"], "SUSPENDED")


if __name__ == "__main__":
    unittest.main()