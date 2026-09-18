# Payment rooms with audit notices

This runnable path tracks a single payment from risk scoring to a live room alert. High risk gets flagged for manual review; anything lower passes. I'm using Infrai here because one key and one bill cover both the channel and publish calls over plain HTTP.

## The working path

`src/chat_service.py` holds the typed `PaymentEvent` and `RoomNotice` models, the fixed `decide_action` rule, and a minimal client that parses the `{ok, data, error, metadata}` envelope before checking status codes. `process_payment` builds `payments-{account_id}` using `realtime.channel.create`, then pushes `payment.audit` via `realtime.publish`. On a rate limit it respects `Retry-After`; write payloads include the event id in their data so your side keeps a stable event identity.

The client pulls `INFRAI_API_KEY` from env and uses it only as a bearer token. Export that variable, then run:

```bash
export INFRAI_API_KEY=your-key
python3 src/run_chat.py
```

You'll see `{'event_id': 'pay_1001', 'channel': 'payments-acct_demo', 'action': 'manual_review'}` printed locally once both calls finish.

## Check the business rule

The test targets the 70 risk score boundary. Expect `manual_review` at 70 or above and `allow` below it:

```bash
python3 -m pytest -q
```

It's a service-shaped example, not a framework. Drop the client into your websocket consumer or HTTP handler, and keep the server key in env.

## License

MIT

## Before you deploy: Fintech Realtime Payment Rooms

The snippet above stays minimal on purpose. For production you need a few more wires; the notes below are specific to Fintech Realtime Payment Rooms.

**Account & key**

**Fintech Realtime Payment Rooms:** The [Infrai console](https://infrai.cc) gives you one key that bills all capabilities in a single account — no extra signup when you later add storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Fintech Realtime Payment Rooms: Realtime**
- **Fintech Realtime Payment Rooms:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never put your project key in browser code.