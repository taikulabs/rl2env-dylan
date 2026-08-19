**fix(browser): validate agent-browser is runnable, not just present**

## Summary
Browser tools no longer break after `hermes update` when a global `agent-browser` install left a dangling symlink. Resolution now validates the binary actually runs and falls through to a working copy instead of caching a dead path. .

**Root cause:** agent-browser's npm `postinstall` (`fixUnixSymlink()`) re-points a *global* install symlink (e.g. `/opt/homebrew/bin/agent-browser`) at our local `node_modules/agent-browser/bin/...` binary. The next `hermes update` wipes `node_modules`, leaving a dangling symlink that `which` still reports but exec fails on with exit 127 — silently killing all 11 browser tools. Confirmed from `node_modules/agent-browser/scripts/postinstall.js` on the pinned 0.26.0, not just the report. Narrow trigger (global npm install + macOS/Linux), which is why it's rare.

The deeper bug is **trust-on-presence**: `shutil.which` / `Path.exists` accept a name that resolves but won't run, and the result gets cached.

## Changes
- `hermes_constants.py`: new `agent_browser_runnable(path)` — resolves the path (a dangling symlink fails `exists()` before any subprocess) and runs `--version` with a 10s timeout; the `"npx agent-browser"` fallback form is trusted without stat.
- `tools/browser_tool.py`: `_find_agent_browser()` validates every candidate before caching it; a dead one is skipped so resolution falls through (PATH → extended PATH → local `.bin` → npx → lazy-install recheck), self-healing the dangling link.
- `hermes_cli/dep_ensure.py`, `nous_subscription.py`: same validation on their presence checks.
- `hermes_cli/doctor.py`: warns "agent-browser found but not runnable (broken symlink?)" instead of reporting OK on a dead link.
- Tests: `TestAgentBrowserRunnable` contract tests + updated 3 resolution tests for the new runnable-gate.

## Why not `--ignore-scripts` (PR #48601)
That stops the symlink hijack but the same postinstall downloads agent-browser's native binary — skipping it risks breaking a fresh local install for the common case to fix a rare one. This resilience fix is OS-agnostic, self-heals, and can't regress the install path.

## Validation
| Scenario | Before | After |
|---|---|---|
| Dangling global symlink in PATH | cached → every browser tool exit 127 | rejected → falls through to working local copy |
| Non-zero/non-exec/hung binary | trusted | rejected |
| `hermes doctor` on dead link | ✓ OK (wrong) | ⚠ "found but not runnable" |

Targeted suites: 258 passed, 0 failed (`test_hermes_constants`, browser homebrew/hardening/lightpanda, dep_ensure, nous_subscription, doctor). Integration E2E confirmed `_find_agent_browser` skips a dangling PATH hit and resolves the working candidate.

## Infographic

![agent-browser-trust-but-verify](https://v3b.fal.media/files/b/0a9f8cbb/fc8VpUvITQ5ftvyVStq2o_fT0Kcl9F.png)