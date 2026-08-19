**fix(security): redact secrets from CDP URLs before writing to logs**

## Summary
Browser CDP discovery URLs no longer leak secrets into the logs. `_resolve_cdp_override()` in `tools/browser_tool.py` was passing raw CDP endpoint URLs straight to `logger.info`/`logger.warning`, so query-string tokens (`?access_token=…`, `?token=…`) and `user:pass@` userinfo were written verbatim.

The global `redact_sensitive_text()` deliberately passes web-URL query params and userinfo through unmasked (OAuth callbacks, magic-link / pre-signed URLs the agent is meant to follow). CDP discovery endpoints are not such a workflow — their tokens are pure credentials — so we opt INTO URL redaction at these specific log sites.

## Changes
- `tools/browser_tool.py`: new `_sanitize_url_for_logs()` that runs `redact_sensitive_text()` then the shared `_redact_url_query_params()` + `_redact_url_userinfo()` helpers from `agent/redact.py`. All 3 CDP log call sites (success, failure, no-`webSocketDebuggerUrl`) pipe URLs/exceptions through it. Return value is unchanged — the connectable URL keeps its token.
- `tests/tools/test_browser_cdp_override.py`: success-path and failure-path tests asserting secrets don't reach the logs.

## Why this shape (follow-up on the original PR)
The original PR shipped a self-contained regex (`_SENSITIVE_URL_QUERY_PARAM_RE` + a `urlsplit`-based userinfo masker). On salvage we swapped it for the existing, battle-tested `agent/redact.py` helpers (ported from ) — same behavior, a wider sensitive-param set (`code`, `key`, `signature`, `jwt`, `session`, `x-amz-signature`, …), and one implementation to maintain instead of two. Extend, don't duplicate.

## Validation
| | Before | After (log) |
|---|---|---|
| query param | `?access_token=super-secret-123456` | `?access_token=***` |
| ws token | `?token=super-secret-123456` | `?token=***` |
| userinfo | `https://user:hunter2pw@cdp…` | `https://user:***@cdp…` |
| exception str | leaks the URL verbatim | masked |
| non-secret URL | — | passed through intact (no over-redaction) |

`scripts/run_tests.sh tests/tools/test_browser_cdp_override.py` → 9 passed. E2E on the real `_resolve_cdp_override` code path (real imports, captured log records): zero secret leaks across success/failure/userinfo, return value unchanged, non-secret URLs untouched.

## Infographic
![infographic](https://v3b.fal.media/files/b/0aa03b6a/RFXFM1-70LzZRcV99FlYQ_aiZGAVb2.png)