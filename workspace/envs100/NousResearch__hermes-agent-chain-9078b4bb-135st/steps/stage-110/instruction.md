**fix(tui): stop a cwd package named utils/proxy/ui from crashing the gateway child**

## Summary
Hermes no longer crashes when launched from a directory that ships its own top-level package named `utils/`, `proxy/`, or `ui/`. The gateway/TUI child was exiting with code 1 (crash loop) because `from utils import atomic_replace` resolved to the user's package instead of Hermes's.

Root cause: `tui_gateway/entry.py` already stripped the *relative* cwd forms (`''`/`'.'`) from `sys.path`, but the launch directory also reaches `sys.path` as its own **absolute** path — via venv activation or a project that adds itself to `PYTHONPATH` (the reporter's `~/downloads/tg-ws-proxy/` is itself a venv). That absolute entry sat ahead of the Hermes root and the strip never caught it. .

## Changes
- `hermes_bootstrap.py`: new `harden_import_path(src_root=None)` — drops the relative cwd forms AND relocates the Hermes source root to the front of `sys.path` even when an absolute cwd entry is already present. Self-anchors on the module's own directory, so it doesn't depend on the spawner exporting an env var.
- `tui_gateway/entry.py`: replaces the inline guard with a call to the shared helper.
- `acp_adapter/entry.py`: calls the helper after the bootstrap import (`hermes acp` can start from any cwd).
- `ui-tui/src/gatewayClient.ts`: also exports `HERMES_PYTHON_SRC_ROOT` to the child (defense in depth).
- `hermes_cli/main.py` and `gateway/run.py` were already safe (they `insert(0, root)`).
- Tests: behavior tests for `harden_import_path` (including the absolute-cwd-path case); `test_entry_sys_path.py` rewritten to assert the entry point wires the real guard instead of re-implementing it inline.

## Validation
E2E from a reporter-style dir (`utils/`, `proxy/`, `ui/`) with the cwd absolute path on `PYTHONPATH`:

| Entry point | Before | After |
|---|---|---|
| `tui_gateway.entry` | ImportError → exit 1 | resolves Hermes `utils.py` |
| `acp_adapter.entry` | shadow `utils` wins | resolves Hermes `utils.py` |

`scripts/run_tests.sh tests/test_hermes_bootstrap.py tests/tui_gateway/test_entry_sys_path.py` → 21 passed. `ui-tui` typecheck clean.

## Infographic

![gateway-cwd-shadow-fix](https://v3b.fal.media/files/b/0a9f8aa5/iyqkATZAvxes33OP4Nqxi_gbvpaUWB.png)