**feat(relay): declare relevance policy to the connector + document the management plane**

## Infographic

![relay-policy-gateway-half](https://v3b.fal.media/files/b/0a9f6bdb/UOp0Huc0Krr_bSO60fds8_lueLuY1l.png)

## The gateway half of Phase 6 Unit ζ — declare the relevance policy to the connector

The Team Gateway connector (`NousResearch/gateway-gateway`) ships a per-instance **relevance gate** (mention-gating / free-response / allow-bots) and a `POST /relay/policy` route to configure it (Unit ζ, merged). This PR is the **gateway side**: project the agent's *existing* relevance config into the connector's platform-agnostic vocabulary and declare it at boot — so the **same** behaviour the agent already applies directly also governs relay delivery, and excluded chatter never wakes a scaled-to-zero agent.

### What it does

- **`relay_relevance_policy()`** — projects the agent's knobs → the generic shape:

  | gateway config | → connector vocabulary |
  |---|---|
  | `require_mention` | `requireAddress` |
  | `free_response_channels` | `freeResponseScopes` |
  | `{PLATFORM}_ALLOW_BOTS ∈ {mentions,all}` | `allowOtherBots` |

  Reads the fronted platform's config block + the bridged top-level keys. Returns `None` when all-default (the connector's absent-row default already matches) or when no concrete platform is fronted.

- **`send_relay_policy()`** — POSTs `/relay/policy` authenticated with the gateway's **own per-gateway upgrade token** (`make_upgrade_token` — the same bearer as the WS upgrade), so the connector attaches the policy to the **authenticated instance**, never a body-asserted id. Re-declares **every boot** (self-healing, full replace — mirrors the `routeKeys` upsert at provision). **Never raises, never blocks boot**: relevance is an optimization layered on the δ/ε authorization gate, so a failed declaration just leaves the connector's prior/quiet policy. Reuses the per-gateway secret + the `/relay/provision` host — **no new inbound surface, no new credential**.

- **`gateway/run.py`** — calls `send_relay_policy()` right after `register_relay_adapter()` succeeds (the secret is resolved by then).

- **`docs/relay-connector-contract.md`** — new **§7** documenting per-instance delivery + the management plane (`/manage/*` + `/relay/policy`) + the relevance-declaration contract; versioning renumbered to §8. The §2/§3 conformance tables are untouched, so `test_contract_doc_conformance` stays green.

### Design notes

- **Reuses the route ζ already built** (`POST /relay/policy`) rather than extending `/relay/provision` — single mechanism, **zero connector change**, and it's the exact path the connector's `gateway_policy_driver.py` E2E already proves.
- **Autodetect over flag**: fires whenever relay is configured + a secret is resolved; no new opt-in knob. All-default config sends nothing.

### Verification

- **+12 unit tests** (`test_relay_policy_send.py`): the projection mapping (incl. comma-string free-response + top-level `require_mention` fallback + the all-default→`None` case) and the send path (token auth, skip-without-secret, skip-when-default, fail-soft on transport error / non-200, skip-when-unconfigured).
- **Full relay suite: 118 pass** (incl. the contract-doc conformance invariant).
- The connector route is already **E2E-proven** vs this gateway's production transport (connector repo, Unit η `gateway_policy_driver.py`); this PR adds the real gateway send-path that pairs with it.

This completes **Phase 6 (Team Gateway per-user isolation)** end to end.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/relay/test_relay_policy_send.py`