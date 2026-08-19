**feat(plugins): add bundled observability/langfuse plugin (salvage of #16845)**

Langfuse tracing ships as a bundled opt-in Hermes plugin.

Salvaged from #16845 (@kshitijk4poor). Plugin implementation is their
work; the activation model was reshaped to fit the existing plugin
system instead of introducing a parallel `optional-plugins/` directory.

## Changes

| File | Change |
|---|---|
| `plugins/observability/langfuse/` | New bundled plugin — `__init__.py` (6 hooks, ~870 LOC), `plugin.yaml`, `README.md` |
| `hermes_cli/config.py` | `OPTIONAL_ENV_VARS` entries for the 3 user-facing Langfuse keys; optional tuning keys in `_EXTRA_ENV_KEYS` |
| `hermes_cli/tools_config.py` | `TOOL_CATEGORIES["langfuse"]` (Cloud + Self-hosted) + `_run_post_setup("langfuse")` |
| `tests/plugins/test_langfuse_plugin.py` | Manifest + discovery + runtime-gate + cache + inert-hooks (10 tests) |

## Why this isn't #16845 as-authored

- **Lives at `plugins/observability/langfuse/`, not `optional-plugins/observability/langfuse/`.** Standalone bundled plugins are already opt-in — discovery only parses each `plugin.yaml`; the Python module isn't imported unless the plugin is in `plugins.enabled`. The new parallel directory solved a problem the existing system already handles.
- **One activation gate, not three.** The original wired `plugins.enabled` + `plugins.langfuse.enabled` + `HERMES_LANGFUSE_ENABLED` in series. Now: the plugin system's own enable/disable decides whether the plugin loads; credentials decide whether hooks trace.
- **`_get_langfuse()` caches with an `_INIT_FAILED` sentinel.** The original called `hermes_cli.config.load_config()` inside `_is_enabled()` on every hook — full YAML parse + deep merge + env expansion, up to hundreds of times per turn on long tool loops. The rewrite reads env once, caches success *or* failure, and short-circuits all subsequent calls.
- **`hermes tools → Langfuse` post-setup opts the bundled plugin into `plugins.enabled` directly** (via `_save_enabled_set`), instead of going through a separate copy-into-user-plugins install flow.

## Activation

```bash
hermes tools                                     # interactive wizard
hermes plugins enable observability/langfuse     # manual
```

## Validation

- `scripts/run_tests.sh tests/plugins/test_langfuse_plugin.py tests/hermes_cli/test_plugins.py tests/hermes_cli/test_plugins_cmd.py tests/hermes_cli/test_tools_config.py` → 171 passed
- E2E with isolated `HERMES_HOME`:
  - plugin discovered at key `observability/langfuse`, `kind=standalone`, `enabled=False` by default
  - `_get_langfuse()` returns `None` without credentials
  - 100 subsequent `_get_langfuse()` calls perform 0 env reads (cache verified)
  - `hermes_cli.config` never imported by the plugin
  - All 5 hook functions no-op cleanly without a client

.