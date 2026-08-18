**fix: prevent agents from starting gateway outside systemd management**

## Problem

An agent session on Telegram was asked to restart the gateway for DNS recovery. It ran:
```
kill 1605 && cd ~/.hermes/hermes-agent && source venv/bin/activate && python -m hermes_cli.main gateway run --replace &disown
```

This killed the systemd-managed gateway process and started a replacement with `&disown`, completely outside systemd's management. The systemd service saw a clean exit (code 0) and with `Restart=on-failure`, didn't restart. The orphaned gateway ran for ~7 hours until it received SIGTERM, at which point nothing restarted it.

## Root Causes

1. **`Restart=on-failure` in systemd service** — clean SIGTERM shutdown exits with code 0, which isn't a 'failure', so systemd never restarts
2. **Agent started gateway with `&disown`** — took it out of systemd management entirely

## Fixes

### Code changes (this PR)
- Add dangerous command patterns to `tools/approval.py` detecting:
  - `gateway run` with `&`, `disown`, or `setsid` (backgrounding)
  - `nohup ... gateway run` (detaching from terminal)
- When detected, the approval message tells the agent to use `systemctl --user restart hermes-gateway` instead
- 6 new tests covering all variants

### Already applied directly (not in this PR)
- Fixed systemd service: `Restart=on-failure` → `Restart=always`, `RestartSec=10`
- Applied the approval.py patterns to main repo immediately
- Restarted gateway via systemd — Telegram, WhatsApp, API server all reconnected