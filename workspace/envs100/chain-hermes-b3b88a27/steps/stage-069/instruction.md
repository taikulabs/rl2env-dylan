**fix(update): survive mid-update terminal disconnect**

## Summary
`hermes update` no longer leaves the venv half-installed when the controlling terminal closes mid-install. The documented workaround ("use screen/tmux") is no longer required.

Addresses the "terminal closed during upgrade = broken install" complaint from the Chinese community feedback thread.

## Changes
- `hermes_cli/main.py`: new `_install_hangup_protection` helper installed at the top of `cmd_update`. Sets `SIGHUP` to `SIG_IGN` (POSIX preserves `SIG_IGN` across `exec()`, so pip and git subprocesses inherit hangup protection) and wraps stdout/stderr with `_UpdateOutputStream` — mirrors output to `~/.hermes/logs/update.log` and absorbs `BrokenPipeError` when the terminal vanishes.
- `cmd_update` body extracted into `_cmd_update_impl` so the wrapper can always restore stdio via `try/finally` even on `sys.exit` or unhandled exceptions.
- `SIGINT` (Ctrl-C) and `SIGTERM` (systemd shutdown) are intentionally not handled — legitimate cancellations.
- Gateway mode is a no-op since `hermes update --gateway` is already detached.
- `tests/hermes_cli/test_update_hangup_protection.py`: 16 new tests covering the stream wrapper, signal install, gateway-mode no-op, log mirror, graceful failure paths, and `_finalize_update_output`.
- `website/docs/getting-started/updating.md`: new "If your terminal disconnects mid-update" section.

## Validation

| | Before | After |
|---|---|---|
| SSH disconnect during pip install | Python process dies, venv half-installed | SIGHUP ignored, install completes |
| Write to closed stdout post-disconnect | `BrokenPipeError` exits process | Absorbed, update continues |
| Terminal output visible after reconnect | Nothing | `tail ~/.hermes/logs/update.log` |
| Ctrl-C during update | Aborts | Aborts (unchanged) |
| `hermes update --gateway` | Works (already detached) | No-op, unchanged |
| `tests/hermes_cli/test_update_hangup_protection.py` | n/a | 16 / 16 pass |
| `tests/hermes_cli/` regression | 2306 pass + 3 pre-existing fails on main | 2306 pass + same 3 pre-existing |

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_update_hangup_protection.py`