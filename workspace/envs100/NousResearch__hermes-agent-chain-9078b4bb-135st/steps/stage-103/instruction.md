**feat(relay): Phase 5 Unit C — wake primitive (gateway side)**

## Phase 5 Unit C — wake primitive (gateway side)

Pairs with `NousResearch/gateway-gateway` Unit C. This side registers a
per-instance **wake URL** and forwards it to the connector at self-provision, so
a suspended gateway can be poked awake when buffered work arrives. The actual
reconnect-and-drain on wake is Unit B's loop — this unit only wires the wake
**signal**.

### What's here
- **`relay_wake_url()` resolver** — `GATEWAY_RELAY_WAKE_URL` env first (Docker/NAS
  stamp), then `gateway.relay_wake_url` in `config.yaml`; mirrors
  `relay_instance_id()` exactly.
- **Forwarded at self-provision** — `_post_provision` adds `wakeUrl` to the JSON
  body **only when set** (absent ⇒ connector stores null, back-compat);
  `self_provision_relay()` resolves, forwards, and logs it.
- **`hermes gateway enroll --wake-url <url>`** — persists `GATEWAY_RELAY_WAKE_URL`
  to `.env` so the runtime forwards it at the next self-provision.
- **Contract doc** — documents the §5.2 wake poke in
  `relay-connector-contract.md` §3.3 (registration, the direct/NAS-independent
  GET, security envelope, rate-limit, no new frame).

### Why a URL (not a frame)
The poke must reach a gateway whose WS is **gone** (suspended). It's an
out-of-band, payload-free, unsigned HTTP GET issued **directly** to the
registered URL — NAS-independent (Q-5.2a). It carries no tenant data and no
inbound; tenant authority is re-established by the authenticated WS upgrade when
the gateway re-dials, so a leaked/guessed `wakeUrl` can at worst spuriously
reconnect **its own** instance — no cross-tenant reach.

### Tests
- `relay_wake_url` resolution (env / config / absent), provision forwarding
  (present + None), `_post_provision` body-only-when-set — **6 new**.
- **130 relay tests pass** (124 prior + 6), **95 contract/conformance pass**.
- Cross-repo E2E `gateway_wake_driver.py` (connector PR) stands up a **real HTTP
  wake endpoint** and proves *buffered ⇒ poke*, rate-limit, and wake⇒reconnect⇒
  drain against this gateway's production transport — **12/12 E2E drivers green**.

Opt-in / default-off: absent `wakeUrl` ⇒ connector never pokes ⇒ today's behaviour.

## Infographic

![wake-primitive-gateway](https://v3b.fal.media/files/b/0a9f83cb/N3N8TOez2Z9miA-0epqzQ_E9JN4K78.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/relay/test_self_provision.py`