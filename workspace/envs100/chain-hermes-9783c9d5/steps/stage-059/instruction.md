**feat(api-server): add basic security headers**

## Summary

Add `X-Content-Type-Options: nosniff` and `Referrer-Policy: no-referrer` to all API server responses via a new `security_headers_middleware`. Standard hardening — prevents MIME sniffing and referrer leakage.

Salvaged from #3383 by @aydnOktay with authorship preserved.

## Changes
- `gateway/platforms/api_server.py`: new `security_headers_middleware`, wired into middleware list
- `tests/gateway/test_api_server.py`: import + wire middleware in test helper, add assertion test

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_api_server.py`