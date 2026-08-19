**feat: show random tip on new session start (CLI + gateway)**

## Summary

Adds a "tip of the day" feature that displays a random one-liner about Hermes Agent features on every new session — both CLI and all gateway messaging platforms.

### What it does
- Shows a random tip from a corpus of **210 curated tips** covering slash commands, keybindings, CLI flags, config options, tools, gateway platforms, profiles, sessions, memory, skills, cron, voice, security, browser, MCP, and more
- **CLI**: tips appear on initial startup, `/clear`, and `/new` in skin-aware dim gold color
- **Gateway**: tips append to the `/new` and `/reset` response on all messaging platforms (Telegram, Discord, Slack, WhatsApp, Signal, Matrix, etc.)
- Fully wrapped in try/except — tips never break startup or reset

### Display format

**CLI:**
```
Welcome to Hermes Agent! Type your message or /help for commands.
✦ Tip: /btw <question> asks a quick side question without tools or history.
```

**Gateway (Telegram, Discord, etc.):**
```
✨ Session reset! Starting fresh.
✦ Tip: hermes -c resumes your most recent CLI session.
```

### Files changed
- **`hermes_cli/tips.py`** (new) — 210-tip corpus + `get_random_tip()` + `get_tip_count()`
- **`cli.py`** — tip display in 3 places: initial startup, /clear with TUI, /clear without TUI
- **`gateway/run.py`** — tip appended to `_handle_reset_command` response
- **`tests/hermes_cli/test_tips.py`** (new) — 12 tests covering corpus quality, randomness, and integration