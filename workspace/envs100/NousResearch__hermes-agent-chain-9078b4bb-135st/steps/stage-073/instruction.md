**feat(computer_use): disable cua-driver telemetry by default, add opt-in**

## Summary

cua-driver ships anonymous usage telemetry (PostHog) **enabled by default** upstream — it fires `cua_driver_install` / `cua_driver_doctor` events to `eu.i.posthog.com`. This makes Hermes disable it for our users unless they explicitly opt in.

## Changes

- **Config**: new `computer_use.cua_telemetry` key in `DEFAULT_CONFIG` (default `false`).
- **Policy helper** (`cua_backend.cua_driver_child_env`): injects `CUA_DRIVER_RS_TELEMETRY_ENABLED=0` into the cua-driver child env when telemetry is disabled (the default); leaves the var untouched on opt-in so the driver uses its own default. Reads config **fail-safe** — any read error defaults to telemetry off.
- **Every spawn site routed through the policy**: MCP backend (`StdioServerParameters` env), `cua_driver_update_check`, the `doctor` `health_report` Popen, the `install.sh`/`install.ps1` runner, and the `--version` / `status` probes.
- **Docs**: new Telemetry subsection in `computer-use.md`.
- **Tests**: `tests/computer_use/test_cua_telemetry.py` — default disables, explicit-false disables, opt-in leaves the var untouched, config-failure fails safe, inherited-enabled is overridden off.

## Opt back in

```yaml
computer_use:
  cua_telemetry: true   # default: false (telemetry off)
```

## Validation

| | Result |
|---|---|
| New telemetry tests + doctor + computer_use + install suites | 213 pass, 0 fail |
| Live Linux (real cua-driver-rs 0.6.0): default | `telemetry: disabled via CUA_DRIVER_RS_TELEMETRY_ENABLED`, **no event sent** |
| Live Linux: opt-in | `[telemetry] sending event: cua_driver_doctor` (driver default) |
| Touched Python files | `py_compile` clean |

 (cross-platform cua-driver), which surfaced that telemetry was on by default.

## Infographic

![telemetry-off-by-default](https://v3b.fal.media/files/b/0a9f5351/LH0OsF6GEDp5PaIXZRaat_IxVBsU2n.png)