**fix: replace hardcoded ~/.hermes paths with get_hermes_home() for profile support**

## Summary

Prep work for the upcoming profiles feature. Profiles give each agent its own HERMES_HOME directory, so all path references must respect the `HERMES_HOME` env var rather than hardcoding `~/.hermes`.

## Changes

**Hardcoded path fixes (3 files):**
- `gateway/platforms/matrix.py` — Matrix E2EE store was hardcoded to `~/.hermes/matrix/store`. Now uses `get_hermes_home()`.
- `gateway/platforms/telegram.py` — Two locations reading config.yaml via `Path.home()/.hermes` instead of `get_hermes_home()`. DM topic persistence and hot-reload would read the wrong config.
- `tools/file_tools.py` — Security path for hub index blocking was hardcoded to `~/.hermes`.

**Service naming improvements (gateway.py):**
- New `_profile_suffix()` helper: detects `~/.hermes/profiles/<name>` → returns profile name; other custom paths → returns hash.
- `get_service_name()` now returns `hermes-gateway-coder` instead of `hermes-gateway-a1b2c3d4` for profile dirs.
- `get_launchd_plist_path()` now scoped per profile: `ai.hermes.gateway-coder.plist`.
- New `get_launchd_label()` — all launchctl commands in gateway.py, main.py, and status.py updated to use it.

**macOS launchd fix (pre-existing bug):**
- Launchd plist was missing `HERMES_HOME` in `EnvironmentVariables`. Custom HERMES_HOME has always been broken on macOS launchd — this fixes it.