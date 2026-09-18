from chat_service import InfraiRealtime, PaymentEvent, process_payment


def main() -> None:
    payment = PaymentEvent("pay_1001", "acct_demo", 1299, "USD", 82)
    action = process_payment(InfraiRealtime(), payment)
    print({"event_id": payment.event_id, "channel": f"payments-{payment.account_id}", "action": action})


if __name__ == "__main__":
    main()
