**fix(dashboard): serve uvicorn on SelectorEventLoop on Windows**

## Summary
On Windows, `hermes dashboard` and `hermes desktop` bind a socket that never accepts connections, so the backend prints "Skipping web UI build" and hangs forever — the port is LISTENING but no TCP handshake completes and `HERMES_DASHBOARD_READY` never fires.

Root cause: `start_server()` serves uvicorn via a bare `asyncio.run(_serve())`, which on Windows uses the default **ProactorEventLoop**. uvicorn's socket-serving stack assumes a **SelectorEventLoop** on win32 — `uvicorn/loops/asyncio.py` forces it, and `uvicorn.Server.run()` threads `config.get_loop_factory()` into its runner for exactly this reason. Driving uvicorn on the proactor loop is the documented incompatibility.

## Changes
- `hermes_cli/web_server.py`: win32-scoped fix. POSIX keeps the exact `asyncio.run(_serve())` it had (its default loop is already SelectorEventLoop / uvloop — nothing to fix). Only on Windows do we mirror `uvicorn.Server.run` and serve on `config.get_loop_factory()` via `uvicorn._compat.asyncio_run`, with a fallback to `WindowsSelectorEventLoopPolicy` for uvicorn < 0.36.
- `tests/test_web_server.py`: two scoped regression tests — win32 takes the loop-factory runner (never bare `asyncio.run`); POSIX takes bare `asyncio.run` (never the Windows branch).

## Scope
Fixes `hermes dashboard` and `hermes desktop` (the Electron app spawns a `hermes dashboard` backend — same `start_server` path). The gateway symptom in the report has a **separate** root cause (the gateway uses no uvicorn) and is intentionally not addressed here.

## Validation
| | Before (Windows) | After (Windows) |
|---|---|---|
| uvicorn event loop | ProactorEventLoop (hangs) | SelectorEventLoop (serves) |
| dashboard / desktop startup | hangs after "Skipping web UI build" | binds + `HERMES_DASHBOARD_READY` |
| POSIX serve path | `asyncio.run(_serve())` | unchanged |

- E2E: real `uvicorn.Server` served on `config.get_loop_factory()` → 200 on `/health`.
- `tests/test_web_server.py` (3) + `tests/hermes_cli/test_dashboard_unified_launch.py` (9) + `tests/hermes_cli/test_dashboard_auth_gate.py` (22): all green.
- ruff clean.

Reported by @jsjyzsh, who offered to test on the affected Windows 10 environment.

## Infographic

![windows-dashboard-hang-fixed](https://v3b.fal.media/files/b/0a9f8c30/2LK_o6b5S41IuPJvUoSoI_ruORSv3a.png)