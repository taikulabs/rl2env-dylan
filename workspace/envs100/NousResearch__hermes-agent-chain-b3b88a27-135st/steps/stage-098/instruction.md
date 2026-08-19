**feat(webhook): direct delivery mode for zero-LLM push notifications**

## Summary
External services can POST to a webhook route and have the payload delivered directly to a user's chat via any gateway platform adapter — zero LLM tokens, sub-second delivery — by setting `deliver_only: true` on the route. Reuses every existing webhook primitive (HMAC auth, rate limits, idempotency, templates, cross-platform dispatch) instead of standing up a second HTTP ingress server.

Motivated by  from the [Antenna](https://antenna.fyi) team — they identified a real gap (no zero-token external push path today) and proposed a parallel HTTP server. This PR closes the same gap additively in the existing webhook adapter with ~100 lines of new product code.

## Changes
- `gateway/platforms/webhook.py` — new `_direct_deliver()` helper + early dispatch branch in `_handle_webhook` when `deliver_only=true`. Startup validation in `connect()` rejects `deliver_only` with `deliver=log` (log-only direct delivery is pointless).
- `hermes_cli/main.py` + `hermes_cli/webhook.py` — `--deliver-only` flag on `hermes webhook subscribe`; list/show output marks direct-delivery routes clearly.
- `website/docs/user-guide/messaging/webhooks.md` — new **Direct Delivery Mode** section with config example, CLI example, response codes, configuration gotchas.
- `skills/devops/webhook-subscriptions/SKILL.md` — documents `--deliver-only` with use cases (bumped to v1.1.0, tags expanded).
- `tests/gateway/test_webhook_deliver_only.py` — 14 new tests.

## Example — config.yaml (Antenna's use case)

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      port: 8644
      secret: global-fallback
      routes:
        antenna-matches:
          secret: antenna-webhook-secret
          deliver: telegram
          deliver_only: true
          prompt: "🎉 New match: {match.user_name} matched with you!"
          deliver_extra:
            chat_id: "{match.telegram_chat_id}"
```

## Example — dynamic subscription via CLI

```bash
hermes webhook subscribe antenna-matches \\
  --deliver telegram \\
  --deliver-chat-id 123456789 \\
  --deliver-only \\
  --prompt "🎉 New match: {match.user_name} matched with you!"
```

## Validation

| Check | Result |
|---|---|
| New tests (`tests/gateway/test_webhook_deliver_only.py`) | 14/14 pass |
| Full webhook suite (existing + new) | 78/78 pass |
| E2E: real aiohttp server + real urllib POST | 200 OK, agent NOT invoked, target `adapter.send()` called with rendered template |
| E2E: duplicate `X-GitHub-Delivery` ID | `status=duplicate`, target called exactly once |
| E2E: CLI `--deliver-only` flag | Writes `deliver_only: true` to subscriptions.json; rejects `--deliver log` combination |
| Startup validation | `deliver_only` + `deliver=log` raises `ValueError` at `connect()` |

## Invariants preserved
- HMAC signature validation (GitHub/GitLab/generic) — still enforced on every POST, verified in tests
- Rate limiting per route — still applies, verified in tests
- Idempotency cache via `X-GitHub-Delivery` / `X-Request-ID` — still applies, verified in tests
- Body size limits, port conflict detection — unchanged
- Agent-mode routes (the existing behaviour, `deliver_only` absent or false) — unchanged, backward compat verified in tests and CLI E2E

## Credit

Problem identified by @H1an1 / [Antenna](https://antenna.fyi) in . That PR proposed a separate 426-line HTTP server with its own bearer-token auth scheme bound to a different port (8643 alongside webhook's 8644). This PR delivers the same capability as a ~100-line extension to the existing webhook adapter, inheriting the stronger HMAC auth and configurable rate limits.