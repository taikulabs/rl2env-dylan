**fix(claw): detect OpenClaw processes before migrate and cleanup (, #8502)**

## Summary

Salvages and combines contributions from PR #8102 (by @fancydirty) and PR #8555 (by @Sertug17) into a single unified fix.

**What this does:** Before `hermes claw migrate` or `hermes claw cleanup` runs, checks for running OpenClaw processes and services, then warns the user. Messaging platforms only allow one active session per bot token — running both simultaneously causes disconnects and (in the cleanup case) can destroy the entire OpenClaw installation when the service recreates an empty skeleton.

### Changes

**`hermes_cli/claw.py`:**
- New `_detect_openclaw_processes()` — unified detection function combining:
  - Cross-platform process scanning (pgrep on Unix, tasklist + PowerShell on Windows) from PR #8102
  - systemd service check (`openclaw-gateway.service`) from PR #8555
  - Returns `list[str]` with details about what was found (empty = nothing detected)
- `_warn_if_openclaw_running()` — called before migration, shows details and prompts
- Cleanup warning block in `_cmd_cleanup()` — called before archival
- Both respect `--yes`, `isatty()`, and non-interactive sessions

**Fixes from original PRs:**
- Removed stray `context_compressor.py` change from #8102
- Fixed `print_warning` calls in #8555 (`print_warning` isn't in claw.py's import chain — used `print_error`/`print_info` instead)
- Added `isatty()` guard to cleanup warning (missing in #8555)
- Removed duplicate `_check_openclaw_running()` — one function serves both commands
- Removed stale `pgrep -f clawd` pattern (too generic, false-positive prone)

**`tests/hermes_cli/test_claw.py`:**
- Updated detection tests for new return type (`list[str]` vs `bool`)
- Added systemd service detection test
- All warning behavior tests updated

### Test Results
47 tests pass.

, .

Co-authored-by: dirtyfancy <fancydirty@gmail.com>
Co-authored-by: Serhat Dolmac <srhtsrht17@gmail.com>