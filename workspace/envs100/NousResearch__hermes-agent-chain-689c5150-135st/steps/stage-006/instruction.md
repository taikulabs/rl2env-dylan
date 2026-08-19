**feat: per-platform display verbosity configuration**

## Summary

Adds per-platform display/verbosity configuration so each messaging channel can have its own verbosity level independently.

**Community request:** Guillaume Meyer wants high verbosity on Telegram (backchannel) and low verbosity on Slack (customer-facing). Nathan Danielsen wants email to have low/no verbosity. This PR makes that possible through `display.platforms` config.

## What changed

### New: `gateway/display_config.py` — resolver module
- `resolve_display_setting(config, platform, key)` — single entry-point for all display settings
- Built-in platform defaults tiered by capability:
  - **High** (telegram, discord): `tool_progress=all`, streaming follows global
  - **Medium** (slack, mattermost, matrix, feishu): `tool_progress=new`
  - **Low** (signal, whatsapp, bluebubbles, wecom, etc.): `tool_progress=off`, `streaming=false`
  - **Minimal** (email, sms, webhook, homeassistant): `tool_progress=off`, `streaming=false`
- Resolution order: platform override > global setting > built-in platform default > fallback

### Config schema (v15 → v16)
New `display.platforms` section:
```yaml
display:
  platforms:
    telegram:
      tool_progress: all
      show_reasoning: true
      streaming: true
    slack:
      tool_progress: off
      show_reasoning: false
    email:
      tool_progress: off
```

Per-platform overrideable settings: `tool_progress`, `show_reasoning`, `tool_preview_length`, `streaming`

### Gateway wiring (`gateway/run.py`)
- Tool progress, tool preview length, streaming, and show_reasoning all resolve per-platform via the new resolver
- `/verbose` command now cycles `tool_progress` per-platform (saves to `display.platforms.<platform>.tool_progress`)
- `/reasoning show|hide` now saves `show_reasoning` per-platform

### Backward compatibility
- Legacy `display.tool_progress_overrides` still read as fallback
- Config migration automatically moves old overrides into `display.platforms`
- YAML 1.1 quirks handled (bare `off` → `False`, etc.)