**fix: /browser connect auto-launch uses dedicated Chrome profile dir**

## Summary

`/browser connect` auto-launches Chrome with `--remote-debugging-port` but was missing `--user-data-dir`. Without it, the launch silently fails when Chrome is already running with the default profile (the common case).

### Changes

- **`_try_launch_chrome_debug()`** — creates `{hermes_home}/chrome-debug/` as a dedicated profile dir and passes `--user-data-dir`, `--no-first-run`, `--no-default-browser-check`
- **Fallback manual instructions** — updated to include the same flags
- **Stale hint removed** — "close existing Chrome windows" replaced with "try again in a few seconds" since the profile conflict is eliminated
- **Tests updated** — shared assertion helper verifies all new flags

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/cli/test_cli_browser_connect.py`