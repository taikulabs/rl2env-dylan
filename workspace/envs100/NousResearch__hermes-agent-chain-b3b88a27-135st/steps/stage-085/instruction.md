**feat: configurable approval mode for cron jobs (approvals.cron_mode)**

## Summary

Adds a new `approvals.cron_mode` config option that controls how cron jobs handle dangerous commands. Previously, cron jobs silently auto-approved all dangerous commands because there was no user present to approve them — a potential security hole.

### New config option

```yaml
approvals:
  mode: manual        # existing — interactive sessions
  cron_mode: deny     # NEW — what to do when nobody can approve
```

**Values:**
- `deny` (default) — block dangerous commands and let the agent find another way
- `approve` — auto-approve everything (previous behavior)

### How it works

When `cron_mode: deny` and a cron job tries to run a dangerous command, the command is blocked and the agent receives:

```json
{"output": "", "exit_code": -1, "status": "blocked", "error": "BLOCKED: Command flagged as dangerous (...) but cron jobs run without a user present to approve it. Find an alternative approach..."}
```

This is identical to what happens when a user clicks "deny" in the CLI — the agent loop continues, it just has to adapt and find another way. The key insight: **the denial doesn't stop the loop**.

### Changes

| File | Change |
|------|--------|
| `hermes_cli/config.py` | Add `approvals.cron_mode: deny` to DEFAULT_CONFIG |
| `cron/scheduler.py` | Set `HERMES_CRON_SESSION=1` env var before agent runs |
| `tools/approval.py` | Add `_get_cron_approval_mode()` helper; modify both `check_command_approval()` and `check_all_command_guards()` to respect cron_mode |
| `tests/tools/test_cron_approval_mode.py` | 21 new tests — config parsing, deny/approve behavior, edge cases |

### Interactions with other mechanisms

- Container environments (docker, modal, etc.) still auto-approve regardless of cron_mode
- `--yolo` / `approvals.mode: off` still overrides cron_mode
- Non-cron, non-interactive sessions (scripted usage) still auto-approve as before
- Safe commands (ls, echo, git, etc.) are never blocked