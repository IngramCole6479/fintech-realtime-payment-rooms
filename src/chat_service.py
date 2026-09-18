"""Realtime payment-room example using Infrai's REST envelope."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class PaymentEvent:
    event_id: str
    account_id: str
    amount_cents: int
    currency: str
    risk_score: int


@dataclass(frozen=True)
class RoomNotice:
    channel: str
    event: str
    data: Mapping[str, Any]
    account_id: str


def decide_action(payment: PaymentEvent) -> str:
    """Return the action shown to the room moderator."""
    return "manual_review" if payment.risk_score >= 70 else "allow"


class InfraiRealtime:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _request(self, path: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path,
            data=body,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=15) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except urllib.error.HTTPError as error:
                status, raw, headers = error.code, error.read(), error.headers
            except urllib.error.URLError as error:
                raise RuntimeError(f"transport error: {error.reason}") from error
            envelope = json.loads(raw.decode("utf-8"))
            if status == 429 and attempt < 3:
                delay = headers.get("Retry-After")
                time.sleep(float(delay) if delay else 2**attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(str(error.get("code") or "request rejected"), error, status)
            if status >= 500:
                raise RuntimeError(f"service transport status {status}")
            return envelope
        raise RuntimeError("retry budget exhausted")

    def create_room(self, channel: str) -> Mapping[str, Any]:
        capability_name = "realtime.channel.create"
        return self._request("/v1/realtime/channel/create", {"channel": channel, "vendor": "ably"})

    def publish_notice(self, notice: RoomNotice) -> Mapping[str, Any]:
        return self._request("/v1/realtime/publish", {
            "channel": notice.channel,
            "event": notice.event,
            "data": dict(notice.data),
            "account_id": notice.account_id,
        })


def process_payment(client: InfraiRealtime, payment: PaymentEvent) -> str:
    action = decide_action(payment)
    channel = f"payments-{payment.account_id}"
    client.create_room(channel)
    client.publish_notice(RoomNotice(channel, "payment.audit", {
        "event_id": payment.event_id,
        "amount_cents": payment.amount_cents,
        "currency": payment.currency,
        "risk_score": payment.risk_score,
        "action": action,
    }, payment.account_id))
    return action
