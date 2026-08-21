**fix(api-server): allow Idempotency-Key in CORS headers (salvage #3384)**

## Summary

Salvage of #3384 by @aydnOktay onto current main.

The API server already reads `Idempotency-Key` from requests for deduplication, but the CORS `Access-Control-Allow-Headers` didn't include it — browser clients would fail preflight when sending this header.

### Changes
- Add `Idempotency-Key` to `_CORS_HEADERS` allow-list
- Add test for `Idempotency-Key` preflight allowance
- Add test for existing `Vary: Origin` behavior

### What was dropped from #3384
The `Vary: Origin` middleware changes were redundant — `_cors_headers_for_origin()` already sets `Vary: Origin` on line 317 (added after #3384 branched).

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_api_server.py`