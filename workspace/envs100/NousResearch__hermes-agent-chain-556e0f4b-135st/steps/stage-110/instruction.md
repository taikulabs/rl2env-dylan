**fix(security): add SSRF protection to browser_navigate**

## Summary

Salvage of PR #3041 by @0xbyt4 — cherry-picked onto current main with two hardening improvements.

`browser_navigate()` had `check_website_access()` (domain blocklist) but was missing `is_safe_url()` (SSRF/private IP check). The agent could navigate the browser to `127.0.0.1`, `169.254.169.254` (cloud metadata), `192.168.x.x`, etc. The other URL-capable tools (`web_tools.py`, `vision_tools.py`) already had this check.

### Follow-up hardening

1. **Fail-closed fallback**: Changed the import fallback from `lambda url: True` (allow all) to `lambda url: False` (block all). Security guards should never fail-open — if the `url_safety` module can't import, block everything rather than allowing SSRF.

2. **Post-redirect SSRF check**: After navigation, verifies the final URL isn't a private/internal address. If a public URL redirected to `169.254.169.254` or localhost, navigates to `about:blank` and returns an error. This prevents the model from reading internal content via subsequent `browser_snapshot` calls. Mirrors the redirect protection already in `vision_tools.py`.

### Tests
6175 passed. 4 pre-existing cron failures (unrelated).

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_website_policy.py`