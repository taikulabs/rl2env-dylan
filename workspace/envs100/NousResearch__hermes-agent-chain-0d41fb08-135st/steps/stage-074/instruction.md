**fix(security): block redirect-based SSRF in Slack image uploads + base.py cache helpers**

## Summary

Salvage of PR #7120 by @Dusk1e, plus follow-up hardening.

**From #7120 (Dusk1e):** Adds an httpx `event_hooks` redirect guard to Slack `send_image()` that re-validates each redirect target via `is_safe_url()`, preventing redirect-based SSRF where a public URL 302s to a private/internal address (e.g. `169.254.169.254`).

**Nit fix:** Renamed `_safe_url_for_log` → `safe_url_for_log` (dropped underscore) since the PR imports it cross-module into the Slack adapter.

**Follow-up:** Applied the same redirect guard pattern to `cache_image_from_url()` and `cache_audio_from_url()` in `base.py` — these had the same pre-flight-only `is_safe_url()` check with unguarded `follow_redirects=True`. Updated `url_safety.py` docstring to reflect broader coverage.

## Files changed
- `gateway/platforms/base.py` — `safe_url_for_log` rename, `_ssrf_redirect_guard` helper, wired into both cache download functions
- `gateway/platforms/slack.py` — updated import to use public name
- `tests/gateway/test_media_download_retry.py` — 3 new SSRF redirect guard tests (image block, audio block, safe passthrough)
- `tests/gateway/test_platform_base.py` — updated to use public name
- `tools/url_safety.py` — docstring update