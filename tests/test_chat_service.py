import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from chat_service import PaymentEvent, decide_action


def test_high_risk_payment_requires_manual_review():
    payment = PaymentEvent("p1", "acct1", 5000, "USD", 70)
    assert decide_action(payment) == "manual_review"


def test_low_risk_payment_is_allowed():
    payment = PaymentEvent("p2", "acct1", 5000, "USD", 69)
    assert decide_action(payment) == "allow"
