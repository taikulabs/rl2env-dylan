**fix: profile paths broken in Docker — profiles go to /root/.hermes instead of mounted volume**

## Summary

In Docker, `HERMES_HOME=/opt/data` (set in Dockerfile) and users mount their `.hermes` directory to `/opt/data`. However, profile operations used `Path.home() / '.hermes'` which resolves to `/root/.hermes` in Docker — an ephemeral container path, not the mounted volume.

**Reported by:** jash5555 on Discord

### What was broken
- `hermes profile create orchestrator --clone` created profile at `/root/.hermes/profiles/orchestrator` (lost on container recreate)
- `active_profile` sticky file written to `/root/.hermes/active_profile` (not on volume)
- `hermes profile list` looked at `/root/.hermes/profiles/` instead of `/opt/data/profiles/`
- Gateway service name helpers also had wrong root detection

### Fix
New `get_default_hermes_root()` function in `hermes_constants.py` (import-safe, no deps) that detects three deployment modes:
1. **Standard** (`HERMES_HOME` unset or under `~/.hermes`) → returns `~/.hermes`
2. **Profile active** (`HERMES_HOME=~/.hermes/profiles/coder`) → returns `~/.hermes`
3. **Docker/custom** (`HERMES_HOME=/opt/data`) → returns `/opt/data`
4. **Docker + profile** (`HERMES_HOME=/opt/data/profiles/coder`) → returns `/opt/data`

All profile path helpers now delegate to this shared function.

### Files changed
- `hermes_constants.py` — new `get_default_hermes_root()`
- `hermes_cli/profiles.py` — `_get_default_hermes_home()` + `_get_profiles_root()`
- `hermes_cli/main.py` — `_apply_profile_override()` + `_invalidate_update_cache()`
- `hermes_cli/gateway.py` — `_profile_suffix()` + `_profile_arg()`