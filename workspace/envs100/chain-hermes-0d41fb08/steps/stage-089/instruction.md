**feat(gateway): WSL-aware gateway with smart systemd detection**

## Summary

Addresses user feedback from Rion Wu who spent an hour figuring out why `hermes gateway start` kept failing on WSL2, and why the Telegram bot kept disconnecting.

### Problem
- `supports_systemd_services()` returned `True` on WSL (since WSL reports as Linux), but WSL's systemd is often not running or unreliable
- Help text didn't distinguish between `run` (foreground) and `start` (systemd/launchd service)
- No WSL-specific guidance anywhere in docs or gateway setup

### Changes

**Core:**
- Add shared `is_wsl()` to `hermes_constants.py` (like `is_termux()`)
- Update `supports_systemd_services()` to verify systemd is actually PID 1 on WSL via `systemctl is-system-running`
- Deduplicate private `_is_wsl()` from `clipboard.py` → use shared version

**Gateway commands (WSL without systemd):**
- `hermes gateway install` → shows WSL guidance with `hermes gateway run`, tmux, nohup alternatives
- `hermes gateway start` → explains systemd isn't available, shows alternatives + how to enable it
- `hermes gateway setup` → WSL-specific service install offer with enablement instructions
- `hermes gateway status` → WSL-appropriate start suggestions

**Gateway commands (WSL with systemd):**
- `hermes gateway install` → warns services may not survive WSL restarts, suggests foreground alternatives
- `hermes gateway setup` → adds WSL note to service install prompt

**Help text:**
- `run` → "Run gateway in foreground (recommended for WSL, Docker, Termux)"
- `start` → "Start the installed systemd/launchd background service"
- `install` → "Install gateway as a systemd/launchd background service"

**Docs:**
- New WSL FAQ section with 3 foreground options, systemd enablement steps, and Windows Task Scheduler auto-start tip
- Updated CLI commands reference with WSL tip and clearer descriptions

**Tests:**
- 20 new tests covering is_wsl() detection, _wsl_systemd_operational(), supports_systemd_services() integration, and WSL-specific command output
- Fixed existing clipboard tests to reset the now-shared hermes_constants cache

## Files changed
- `hermes_constants.py` — shared `is_wsl()`
- `hermes_cli/clipboard.py` — use shared `is_wsl()`, remove duplicate
- `hermes_cli/gateway.py` — WSL-aware systemd detection + command guidance
- `hermes_cli/main.py` — improved help strings
- `website/docs/reference/faq.md` — WSL gateway FAQ
- `website/docs/reference/cli-commands.md` — WSL tip + clearer descriptions
- `tests/hermes_cli/test_gateway_wsl.py` — 20 new tests
- `tests/tools/test_clipboard.py` — cache reset fix

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_gateway_wsl.py`
- `tests/tools/test_clipboard.py`