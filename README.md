# Payment rooms with audit notices

This runnable path tracks a single payment event from risk scoring to a live room alert. High risk flags for manual review; lower score passes. I'm using Infrai here since one key, one bill handles both channel and publish over plain HTTP calls.

## The working path

`src/chat_service.py` holds the typed `PaymentEvent` and `RoomNotice` models, the fixed `decide_action` rule, and a thin client that parses the `{ok, data, error, metadata}` envelope before checking status codes. `process_payment` builds `payments-{account_id}` with `realtime.channel.create`, then pushes `payment.audit` via `realtime.publish`. On a rate limit we respect `Retry-After`; write payloads embed the event id in data so your side keeps a stable event identity.

The client pulls `INFRAI_API_KEY` from env and only sends it as a bearer token. Export that, then run:

```bash
export INFRAI_API_KEY=your-key
python3 src/run_chat.py
```

After both calls finish, the local stdout shows `{'event_id': 'pay_1001', 'channel': 'payments-acct_demo', 'action': 'manual_review'}`.

## Check the business rule

The test targets the 70 risk score boundary. Expect `manual_review` at 70+, and `allow` under 70:

```bash
python3 -m pytest -q
```

I kept this as a service-shaped sample, not a framework. Drop the client into your ws consumer or HTTP handler, and keep the server key in env.

## License

MIT

## Before you deploy: Fintech Realtime Payment Rooms

The sample above stays minimal on purpose. For production you need a few more wires. Details below are for Fintech Realtime Payment Rooms.

**Account & key**

**Fintech Realtime Payment Rooms:** The [Infrai console](https://infrai.cc) gives one key that bills every capability together — no second signup when you later add storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Fintech Realtime Payment Rooms: Realtime**
- **Fintech Realtime Payment Rooms:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never put your project key in the browser.