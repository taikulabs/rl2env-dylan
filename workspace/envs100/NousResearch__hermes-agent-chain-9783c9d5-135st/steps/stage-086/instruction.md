**fix(banner): show honcho tools as available when configured**

## Summary

Fixes honcho tools showing as red/disabled in the startup banner even when properly configured.

### Problem

The honcho `check_fn` only checked runtime session state (`_session_manager is not None`), which isn't injected until `AIAgent.__init__()`. The banner renders before agent construction, so honcho tools always appeared unavailable at startup.

### Fix

Updated `_check_honcho_available()` in `tools/honcho_tools.py` to check configuration as a fallback:

1. **Fast path** (unchanged): if session context is active, return True immediately
2. **Slow path** (new): if no session, load `HonchoClientConfig.from_global_config()` and check `enabled + api_key/base_url`
3. **Graceful fallback**: if `honcho_integration` isn't installed, return False

This correctly reflects "will honcho work once the session starts?" rather than "is honcho running right now?"

### Tests

4 new tests in `test_honcho_tools.py`:
- Session active → True
- Configured but no session (banner time) → True
- Not configured → False
- Import failure (package not installed) → False

 (took the intent, implemented differently — the original PR had a dict key bug and the delegate_tool change was stale).