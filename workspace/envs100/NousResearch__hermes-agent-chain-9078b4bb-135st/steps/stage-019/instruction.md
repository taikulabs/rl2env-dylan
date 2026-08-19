**feat(gateway): typed send-error classification (SendResult.error_kind)**

## Summary
Send failures now carry a machine-readable category so consumers can branch on a typed reason instead of substring-matching the raw provider message.

Adds a platform-neutral `error_kind` to `SendResult` plus a shared classifier; wires it into the Telegram adapter's `send()` failure path. Purely additive — no behavioral change to any existing delivery path.

## Changes
- `gateway/platforms/base.py`: `SEND_ERROR_KINDS` vocabulary (`too_long` / `bad_format` / `forbidden` / `not_found` / `rate_limited` / `transient` / `unknown`) + `classify_send_error(exc, error_text)`. New optional `SendResult.error_kind` field defaults to `None` (backward compatible — existing call sites unchanged).
- `plugins/platforms/telegram/adapter.py`: populate `error_kind` on `send()` failures; the existing `message_too_long` token is preserved and now also carries `error_kind="too_long"`.
- `tests/gateway/test_send_error_classification.py`: 22 tests (classifier vocabulary + Telegram wiring).

## Design notes
- Conservative classifier: anything unrecognized → `"unknown"`, so a consumer never mistakes an unclassified failure for a benign one.
- The existing degrade-and-deliver behavior is untouched — MarkdownV2→plain-text fallback, overflow split, and retry classification all still run. No user-facing notice is forced: Telegram's `send()` already recovers parse errors via plain-text fallback, so surfacing a notice would be noise on an already-correct path. `error_kind` is additive observability/branching surface.

## Validation
| | Before | After |
|---|---|---|
| `SendResult` consumers | substring-match raw `error` | branch on typed `error_kind` |
| Telegram `send()` failure | free-form `error` string only | `error` + `error_kind` |
| Tests | — | 22 new + 210 adapter regression green |

## Infographic

![typed-send-error-classification](https://v3b.fal.media/files/b/0a9f3899/PgRPL92ov5pinHQxqMMK9_KDGPEHpp.png)