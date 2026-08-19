**fix: improve profile creation UX — seed SOUL.md + credential warning**

## Summary

Addresses user confusion reported in Discord about:
1. New profiles using the wrong model/plan tokens (root cause: no separate API keys)
2. SOUL.md not being read consistently (root cause: no SOUL.md in fresh profiles until first use)

## What changed

**`hermes_cli/profiles.py`** — `create_profile()` now seeds a default SOUL.md immediately after creating the directory structure. Skipped when the profile already has one (from `--clone` / `--clone-all`).

**`hermes_cli/main.py`** — Post-creation output for fresh profiles (no `--clone`) now:
- Warns that the profile has no API keys and will inherit from the shell environment
- Shows the SOUL.md path for personality customization
- Moved `profile_dir_display` computation to cover both clone and non-clone paths

## Before
```
Profile 'mybot' created at ~/.hermes/profiles/mybot
42 bundled skills synced.

Next steps:
  mybot setup              Configure API keys and model
  mybot chat               Start chatting
  mybot gateway start      Start the messaging gateway
```

## After
```
Profile 'mybot' created at ~/.hermes/profiles/mybot
42 bundled skills synced.

Next steps:
  mybot setup              Configure API keys and model
  mybot chat               Start chatting
  mybot gateway start      Start the messaging gateway

  ⚠ This profile has no API keys yet. Run 'mybot setup' first,
    or it will inherit keys from your shell environment.
  Edit ~/.hermes/profiles/mybot/SOUL.md to customize personality
```

## Investigation findings (issue #8093)

E2E verified that `load_soul_md()` correctly reads from the profile's HERMES_HOME. The code path is:
- `_apply_profile_override()` sets `HERMES_HOME` before module imports
- `load_soul_md()` calls `get_hermes_home() / "SOUL.md"` which reads the env var
- Both CLI and gateway paths resolve correctly

Issue #8093's reporter showed identical files in both locations (diff produces no output), so their "cross-contamination" conclusion was unsupported by evidence. Closed with detailed analysis.