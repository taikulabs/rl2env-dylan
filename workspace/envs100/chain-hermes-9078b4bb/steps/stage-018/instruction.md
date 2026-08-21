**feat(hindsight): configurable embedded daemon health grace timeout**

## Summary
Users on busy / low-resource hosts can now raise the embedded Hindsight daemon's health grace timeout from `config.json` instead of hand-setting a raw env var, so a momentarily-slow daemon under load isn't needlessly killed and restarted.

Background: the embedded daemon's `/health` is checked with a hardcoded 2s timeout upstream. On contended hosts a busy daemon can exceed that for a single check; upstream `hindsight-embed` already waits a grace window (`HINDSIGHT_EMBED_PORT_HEALTH_GRACE_TIMEOUT`, default 30s) before treating it as stale and killing+restarting — but that env var is read into a module-level constant *at import time*, and there was no Hermes-side way to set it short of exporting the raw var. Reported in the #13125 comment thread (@GusBot69's production deployment).

## Changes
- `plugins/memory/hindsight/__init__.py`:
  - New `port_health_grace_timeout` config option. `initialize()` exports it to `HINDSIGHT_EMBED_PORT_HEALTH_GRACE_TIMEOUT` **before** `daemon_embed_manager` is imported (the import-time read is the contract). `os.environ.setdefault` so an operator's explicit env override always wins. Invalid / negative / blank values are ignored (fall back to upstream's 30s).
  - Surfaced in `hermes memory setup` for `local_embedded` mode, and documented in the module env-var header.
- `tests/plugins/test_hindsight_health_grace_timeout.py`: new — covers value export, string parsing, blank/missing no-op, invalid/negative ignored, and env-override precedence.

## Validation
| input | result |
|---|---|
| `port_health_grace_timeout: 60` | env `= 60.0` |
| env already set | env override wins (config ignored) |
| blank / missing / invalid / negative | no-op → upstream 30s default |

- `scripts/run_tests.sh tests/plugins/test_hindsight_health_grace_timeout.py` → 5 passed
- E2E in a real interpreter: env var is set **before** the runtime/daemon-manager import (ordering contract holds).
- ruff clean, base 0 behind main.

Note: the underlying 2s `is_running()` check and the kill decision live in the third-party `hindsight-embed` package, not in this repo — the worst of the loop (killing on one slow check) is already mitigated upstream via the grace window. This PR is the Hermes-side lever to tune that window.

## Infographic

![hindsight-health-grace-timeout](https://v3b.fal.media/files/b/0a9f389a/bqlK3mHZ7bjR7vrh2XBOq_LcYbh4D1.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/plugins/test_hindsight_health_grace_timeout.py`