**fix(email): make pairing opt-in, ignore unknown senders by default**

## Summary
Email now silently ignores unknown senders by default instead of replying to arbitrary unread inbox messages with pairing codes.

An agent mailbox can contain unrelated human email, so the generic DM "pair" default could leak pairing prompts to unintended senders on reconnect/startup polling. Email is inbox-shaped, not chat-shaped — pairing must be explicit opt-in.

## Changes
- `gateway/config.py` + `gateway/authz_mixin.py`: both resolution layers short-circuit `Platform.EMAIL → "ignore"` unless `platforms.email.unauthorized_dm_behavior: pair` is set. A global default does not opt email into pairing.
- `hermes_cli/gateway.py`: email-specific setup prompt (default = keep unknown senders silent); writes the explicit `pair` override only when chosen; uses the existing `EMAIL_ALLOW_ALL_USERS` flag for open access.
- `hermes_cli/config.py`: extracts a shared `write_platform_config_field` helper; `web_server.py` reuses it.
- Docs: email / security / configuration pages call out the email exception.

## Validation
| Case | Result |
|---|---|
| email, global=pair, no override | `ignore` |
| email, explicit per-platform `pair` | `pair` |
| email, global=ignore | `ignore` |
| telegram default (regression guard) | `pair` |

- Targeted suite: `tests/gateway/test_unauthorized_dm_behavior.py tests/gateway/test_config.py tests/hermes_cli/test_config.py` → 206 passed
- E2E with real imports against temp `HERMES_HOME`: both `GatewayConfig.get_unauthorized_dm_behavior` and `_get_unauthorized_dm_behavior` verified across all cases above

Salvage of #48219 by @shannonsands, cherry-picked onto current main with authorship preserved.

## Infographic

![email-pairing-opt-in](https://v3b.fal.media/files/b/0a9f448c/LImM0126ZDXhOlIYSL6xW_sJFrI6GY.png)