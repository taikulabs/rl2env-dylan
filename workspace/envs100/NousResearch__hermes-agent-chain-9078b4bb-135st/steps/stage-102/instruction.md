**feat(relay): Phase 5 §5.3 going-idle / buffered-flip primitive (gateway side)**

## Phase 5 §5.3 — going-idle / buffered-flip primitive (gateway side)

The **gateway half** of the going-idle/buffered-flip primitive. This is a **scale-to-zero PRIMITIVE, not the behaviour** — nothing here decides to sleep or suspends a machine. It integrates with the gateway's **EXISTING drain transition** rather than introducing a parallel relay-only idle path.

### What it does

When the gateway drains, it tells the connector to flip its destination to buffered-only so inbound that arrives while it's gone is buffered durably and replayed (in order, no loss/dup) when it reconnects — instead of being pushed at a closing socket.

- **`ws_transport.py`**
  - `go_idle()` — sends `going_idle`, awaits the connector's `going_idle_ack` (connector-authoritative flip-then-ack, **Q-5.3c**: stays serving until the ack, so an event in the flip window is delivered live, not lost). Returns `False` on timeout/not-connected (caller closes anyway — no regression).
  - Buffered inbound (a delivery carrying a `bufferId`) is acked via `inbound_ack` **after** the handler runs → drain-without-dup on the delivery leg.
  - **NET-NEW reconnect loop** — re-dials + re-handshakes after an *unexpected* close (capped backoff), so a gateway that went idle re-establishes its socket, which triggers the connector's buffered-flip drain. Off by default; `register_relay_adapter` turns it on in production. A *deliberate* `disconnect()` never reconnects.
- **`adapter.py`** — emits `going_idle` from its existing `disconnect()` drain seam before tearing down the socket; best-effort + guarded (a missing `go_idle`, or a failed/timed-out ack, never blocks shutdown).
- **`transport.py`** Protocol + **`docs/relay-connector-contract.md` §3.2** document the three new frames.

### Not in scope (deferred behaviour)

The autonomous idle timer that *decides* to drain, the actual machine suspend (Fly `autostop:"suspend"`), and the NAS suspended-health model. A future workstream consumes these primitives.

### Verification

- **+6 relay unit tests** (`tests/gateway/relay/test_relay_going_idle.py`); full relay suite **124 pass**.
- Cross-repo E2E: the connector's new `gateway_going_idle_driver.py` drives this production transport through go-idle → ack → flip → buffer-while-disconnected → reconnect → drain-replay-in-order → **no loss / no dup** → unflip over a **real socket**. All 11 drivers green.

> **Merge ordering:** this is the FIRST half. The connector PR (`NousResearch/gateway-gateway` `feat/phase5-b-going-idle`) adds an E2E driver that imports `go_idle`/reconnect from this branch, so its cross-repo CI stays red until this lands. Land this, then the connector.

Ben's relay-adapter solo lane.

## Infographic

![phase5-going-idle-spine](https://v3b.fal.media/files/b/0a9f8172/BKHAzB40WAlMsxQq7IH0r_9fIim67K.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/relay/test_relay_going_idle.py`