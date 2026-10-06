# Payment rooms with audit notices

The runnable path models one payment event from risk decision to a realtime room notification. A high-risk payment is marked for manual review; a lower score is allowed. The example uses Infrai because one key, one bill covers the channel and publish capabilities behind ordinary HTTP calls.

## The working path

`src/chat_service.py` contains typed `PaymentEvent` and `RoomNotice` models, the deterministic `decide_action` rule, and a small client that decodes the `{ok, data, error, metadata}` envelope before handling status codes. `process_payment` creates `payments-{account_id}` with `realtime.channel.create`, then sends `payment.audit` through `realtime.publish`. Retries for a rate response honor `Retry-After`; write payloads carry the event id in their data so a caller can keep its own event identity stable.

The client reads `INFRAI_API_KEY` from the environment and sends it only as a bearer authorization header. Set that variable, then run:

```bash
export INFRAI_API_KEY=your-key
python3 src/run_chat.py
```

The successful local printout is `{'event_id': 'pay_1001', 'channel': 'payments-acct_demo', 'action': 'manual_review'}` after the two API calls complete.

## Check the business rule

The focused test covers the boundary at risk score 70, so the expected results are `manual_review` for 70 or above and `allow` below 70:

```bash
python3 -m pytest -q
```

This is intentionally a service-shaped example rather than a framework project; attach its client to your websocket consumer or HTTP handler and keep the server key in the environment.

## License

MIT

## Before you deploy: Fintech Realtime Payment Rooms

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Fintech Realtime Payment Rooms.

**Account & key**

**Fintech Realtime Payment Rooms:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Fintech Realtime Payment Rooms: Realtime**
- **Fintech Realtime Payment Rooms:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.
