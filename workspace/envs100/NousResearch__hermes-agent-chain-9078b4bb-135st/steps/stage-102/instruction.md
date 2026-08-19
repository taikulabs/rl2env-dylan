**fix(gateway): refuse model switch on stale checkout to avoid env_float ImportError**

## Summary
Switching a live gateway session's model after the checkout was updated underneath it (e.g. a manual `git pull`) now returns a clear "restart the gateway" message instead of crashing on `cannot import name 'env_float' from 'utils'`.

Root cause: the gateway is a single long-lived process, so its `sys.modules` is frozen at boot. `env_float` was added to `utils.py` and ~22 consumer modules in the same release (06ca1e998, 2026-06-20). A process that booted before that, then had its source updated on disk, still holds the old `utils` in memory. Switching to a different provider forces the first-time lazy import of a consumer module on the new code path — its freshly-pulled `from utils import env_float` resolves against the stale cached `utils` and raises ImportError. The on-disk file is fine, which is why the error is so confusing.

`hermes update` already gracefully restarts gateways after a pull, so this only bites when code changes outside that flow or in the window before the restart fires. Rather than chase per-module reloads (fragile) or force an auto-restart that drains the session, the gateway now snapshots its git revision at boot and refuses the model switch with a clear message if the checkout drifted. Scoped to model switching deliberately — the known, highest-risk trigger (it reliably forces a new lazy import path on a provider switch).

## Changes
- `gateway/code_skew.py` (new): snapshots the checkout git-rev at boot via the existing worktree-aware `_read_git_revision_fingerprint`; `detect_code_skew()` returns short `(boot, disk)` labels if the checkout drifted. No-ops cleanly on non-git installs and unreadable revs (never a false positive).
- `gateway/run.py`: calls `record_boot_fingerprint()` at the top of `start_gateway()`.
- `gateway/slash_commands.py`: new `_model_switch_skew_guard()` early-returns its message before both model-switch entry points (the picker callback and the direct `/model <name>` path).
- `tests/test_stale_utils_module_import.py` (new): reproduces the exact ImportError mechanism and shows the messaging client is incidental.
- `tests/test_code_skew.py` (new): covers detection (drift, no-drift, non-git no-op, idempotency) and the guard message.

## Validation
| | Before | After |
|---|---|---|
| `/model` after hot `git pull` | `ImportError: cannot import name 'env_float' from 'utils'` | "This gateway is running code from <rev> but the checkout on disk is now <rev>. … restart the gateway: hermes gateway restart" |
| Non-git / unreadable rev | (n/a — crashed on switch anyway) | Skew detection no-ops; no false positive |
| Tests | — | 13 new tests pass; E2E reproduction + guard verified against fresh main |