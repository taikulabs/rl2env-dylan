**fix(moa): disabled presets no longer hijack a plain model switch**

## Summary
A disabled MoA preset can no longer silently pivot a session onto the MoA virtual provider via a plain model switch.

## Changes
- `hermes_cli/moa_config.py`: `exact_moa_preset_name` now gates the match on the per-preset `enabled` flag — a disabled preset returns no match.
- `tests/hermes_cli/test_moa_config.py`: regression tests for disabled-preset skipping + enabled-preset still matching.

## Root cause
`exact_moa_preset_name` matched any bare model name equal to a preset key regardless of `enabled`. On the no-explicit-provider switch path (PATH B in `model_switch.py`), a routine `/model <name>` whose name collided with a preset key (e.g. `default`) silently set `target_provider = "moa"` — even when the user had set `enabled: false` to opt out. The hijacked session could land on a broken MoA provider (empty `default_preset`, unconfigured aggregator credentials), and subsequent `/model` calls failed.

Explicit selection via `--provider moa` / the model picker uses PATH A and does not go through `exact_moa_preset_name`, so a disabled preset stays reachable when the user explicitly asks for it.

## Validation
| | Before | After |
|---|---|---|
| `/model default`, preset `default` `enabled: false` | pivots to `provider=moa` | resolves as a normal model |
| `/model fast`, preset `fast` `enabled: true` | matches preset | matches preset (unchanged) |
| picker `<preset> --provider moa` (explicit) | works | works (unchanged) |
| `test_moa_config.py` | — | 17 passed, 0 failed |

.

## Infographic
![MoA preset opt-out fix](https://v3b.fal.media/files/b/0aa05cac/TkLq3Zk5auCA-ty8moHqW_0KpQ6JAp.png)

---
Nous Research