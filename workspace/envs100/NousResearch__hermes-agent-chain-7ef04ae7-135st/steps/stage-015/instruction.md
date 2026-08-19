**fix(windows): cover remaining console-flash spawn legs**

## Summary
Covers the remaining high-signal Windows console-flash spawn legs reported after #54236: slash-worker Python spawns, gateway restart watchers, Git Bash `ps.exe` fallbacks, eager browser startup probes, and node/agent-browser version checks.

## Changes
- `tui_gateway/server.py`: `_SlashWorker` now launches hidden on Windows.
- `gateway/run.py`: gateway `/restart` watcher prefers `pythonw.exe` so crash/restart loops do not flash console `python.exe` windows.
- `gateway/status.py`, `hermes_cli/gateway.py`: Windows process-inspection paths skip Git Bash `ps.exe` fallback and use psutil instead.
- `tools/browser_tool.py`: Desktop/browser tool-schema checks use a lightweight agent-browser lookup, so startup no longer runs `agent-browser.CMD --version`; actual browser execution still validates before use.
- `hermes_constants.py`: node and agent-browser `--version` probes carry `windows_hide_flags()`.
- Added regression coverage for the new hidden-spawn and no-ps paths.

## Tracker update
Added a #54220 comment folding in the latest related reports and PRs: #54392, #54364, #54323, #54282, #54082, #54342, #53555, #53539, #53173, #51759, plus overlapping PRs #53879, #53291, #53542, #53358.

## Validation
| Check | Result |
|---|---|
| Targeted tests | `scripts/run_tests.sh tests/tools/test_browser_chromium_check.py tests/tools/test_browser_homebrew_paths.py tests/tools/test_browser_hardening.py tests/test_hermes_constants.py tests/gateway/test_status.py tests/gateway/test_restart_drain.py tests/test_windows_subprocess_no_window_flags.py tests/hermes_cli/test_gateway.py -q` → 314 passed |
| Syntax | `python3 -m py_compile ...` on changed files |
| Ruff | clean on changed files |
| Whitespace | `git diff --check` clean |

## Infographic
![windows-console-flash-followup](https://v3b.fal.media/files/b/0aa02622/1Nv0_ltysB9KT30h2ssWq_uB7rGQLJ.png)