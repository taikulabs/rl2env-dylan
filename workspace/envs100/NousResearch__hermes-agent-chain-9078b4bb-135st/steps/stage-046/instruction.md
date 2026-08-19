**fix(terminal): make hermes install dir reachable in subshell PATH**

## Summary
Bare `hermes` now resolves inside the terminal tool's subshell even when the gateway was launched without the hermes install dir on PATH (systemd, service managers, cron, desktop launchers).

Root cause: the terminal subshell PATH was the agent process PATH plus a static set of system dirs (`_SANE_PATH`); it never included wherever the `hermes` console-script actually lives (`~/.local/bin`, the venv `bin`/`Scripts`, pipx, nix). A plugin shelling out to bare `hermes` via `dispatch_tool("terminal", ...)` hit `command not found` (exit 127) — even though `hermes` works in the user's own interactive terminal, which sources the shell rc that exports that dir.

## Changes
- `tools/environments/local.py`: add `_resolve_hermes_bin_dir()` (resolves once via `shutil.which` → `sys.argv[0]` → `sys.executable`'s dir, cached) and `_prepend_hermes_bin_dir()`; `_make_run_env` prepends-if-missing the resolved dir to the subshell PATH. Cross-platform (`os.pathsep`); no-op when unresolvable.
- `tests/tools/test_local_env_blocklist.py`: 7 new tests (resolution paths, idempotence, no-op-when-unresolved, `_make_run_env` injection); scope-fence the existing sane-path tests so a real `hermes` on the runner's PATH doesn't shift their asserted layout.

## Validation
| | Before | After |
|---|---|---|
| `hermes ...` via terminal tool, gateway launched w/o install dir on PATH | exit 127 `command not found` | resolves, exit 0 |
| sane-path merge / Windows PATH behavior | unchanged | unchanged |

E2E: ran `LocalEnvironment.execute("hermes --version")` under a stripped `PATH=/usr/bin:/bin` → rc 0 with real version output. Isolated test with bashrc-sourcing disabled and `which` returning None → injector alone resolves a hermes shim via `sys.executable`'s dir. Tests: 35/35 in the file.

Reported by Smithangshu (plugin author hitting exit 127 on `ctx.dispatch_tool("terminal", {"command": "hermes kanban create ..."})`). Plugins can still belt-and-suspenders with `resolve_hermes_bin()` / `python -m hermes_cli.main`, but bare `hermes` now just works.

## Infographic

![hermes-terminal-path-rescue](https://v3b.fal.media/files/b/0a9f42ac/wV1dy8XbNr-ezaRrlh914_sRzQXSAI.png)