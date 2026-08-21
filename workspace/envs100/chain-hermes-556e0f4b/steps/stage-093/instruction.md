**fix(security): add SSRF protection to vision_tools and web_tools (hardened)**

## Summary

Salvage of PR #2630 by @dieutx with security hardening on top.

**Original contribution (cherry-picked with authorship preserved):**
- New `tools/url_safety.py` module with `is_safe_url()` — resolves hostnames via DNS and blocks private/internal IP ranges
- Integration into `vision_tools.py`, `web_tools.py` (extract + both crawl paths)
- 13 tests in `test_url_safety.py`, updated existing vision test

**Hardening additions:**

| Issue | Fix |
|-------|-----|
| Fail-open on DNS errors and exceptions | Changed to **fail-closed** (OWASP best practice) |
| CGNAT range (100.64.0.0/10) not blocked | Added explicit check — `is_private` returns False for this range |
| Multicast (224.0.0.0/4) not blocked | Added `is_multicast` and `is_unspecified` checks |
| Redirect-based SSRF bypass in vision_tools | Added httpx event hook that re-validates each redirect target |
| Parallel/Tavily extract paths unprotected | Moved SSRF filter **before** backend dispatch |
| DNS rebinding (TOCTOU) | Documented as known limitation (requires connection-level fix) |

**Verified:**
- Live PTY testing: web_extract + vision_analyze work with public URLs, correctly block localhost/169.254.169.254
- Full test suite: 6044 passed, 0 failed
- Alternative IP encodings (decimal, hex, octal, shortened) all caught by getaddrinfo normalization
- IPv4-mapped IPv6 (::ffff:127.0.0.1) correctly blocked on Python 3.13

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_url_safety.py`
- `tests/tools/test_vision_tools.py`
- `tests/tools/test_website_policy.py`