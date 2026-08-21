**feat(relay): forward stable instance id at self-provision (Phase 6 Unit α)**

## Phase 6 Unit α — forward a stable instance id at self-provision (gateway half)

Gateway half of **Phase 6 Unit α**. Lets a hosted/managed gateway tell the connector its stable per-instance id so the connector can bind `gatewayId → instanceId` and route inbound **per-instance** (not tenant-broadcast) once Phase 6 delivery lands — the fix for the confirmed cross-user leak under one-org-one-guild-many-users.

### What
- New `relay_instance_id()` reader: env `GATEWAY_RELAY_INSTANCE_ID` first, then `gateway.relay_instance_id` in config.yaml — mirroring the existing relay readers (`relay_endpoint`, `relay_route_keys`, …).
- `_post_provision` / `self_provision_relay` forward it in the `/relay/provision` body, **only when present** (omitting it lets the connector store null — back-compat for self-hosted / pre-Phase-6 gateways).

### Trust
Gateway-asserted but safely scoped: the org/tenant stays NAS-token-verified at the connector, so a dishonest gateway can only bind **its own** tenant's instance — same posture as `relay_endpoint()` (decisions.md Q11 = Option A). For a managed agent the id is NAS's `AgentInstance.id`, stamped into the container env beside `GATEWAY_RELAY_URL`.

### Tests (106 relay tests pass)
- reader: env / config / absent
- `self_provision_relay` forwards the id (set + absent)
- the real `_post_provision` body includes `instanceId` **only when set**
- Proven end-to-end against the real connector route via the connector repo's cross-repo E2E (`instance_id_bound: PASS`).

### Merge order
Land this **before** the connector PR (NousResearch/gateway-gateway) — the connector's `cross-repo-e2e` job checks out hermes-agent `main` and needs `GATEWAY_RELAY_INSTANCE_ID` forwarding present here first.

Cross-repo siblings: gateway-gateway (connector bind) + nous-account-service (NAS stamp).

_Design: `~/nous/specs/gateway-gateway` plan.md Phase 6 Unit α; decisions.md Q11. Relay adapter is Ben's solo lane._

## Infographic

![phase6 unit alpha - relay instance id](https://v3b.fal.media/files/b/0a9f4ff3/KHDYuP9xlfIOkOWqMwwOM_UH90yI9Q.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/relay/test_self_provision.py`