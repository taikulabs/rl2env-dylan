**fix(api-server): stop silently promising async delivery on stateless HTTP path**

## Summary
`terminal(notify_on_complete=True)` / `watch_patterns` and `delegate_task(background=True)` now refuse to make a delivery promise on the API server / WebUI path instead of silently no-op'ing.

Root cause: the API server is stateless request/response. Every route — the OpenAI-spec `/v1/chat/completions` and `/v1/responses`, *and* the proprietary `/v1/runs` SSE stream — tears down its channel when the turn ends, and `APIServerAdapter.send()` is a no-op stub. A background completion that finished *after* the response closed had nowhere to go. From the agent's side this was indistinguishable from a hang. (The contextvar-registration half of the originally-filed cause was already fixed on main; the remaining gap was delivery, which has no spec-compliant surface on a stateless HTTP client.)

Rather than wire dead delivery machinery into a channel that can't carry it, make the no-op honest.

## Changes
- `gateway/platforms/base.py`: new capability flag `supports_async_delivery` (default `True`). Toggle on the adapter — a future stateless adapter is correct-by-default, not silently broken.
- `gateway/platforms/api_server.py`: `APIServerAdapter.supports_async_delivery = False`; both `_run_agent` paths bind `async_delivery=False`.
- `gateway/session_context.py`: `_SESSION_ASYNC_DELIVERY` contextvar + `async_delivery_supported()` helper; `async_delivery` param on `set_session_vars` (default `True`, cleared to the unset sentinel so a cleared context defaults to supported).
- `gateway/run.py::_set_session_env`: propagates the active adapter's flag into the contextvar (getattr-guarded for bare-runner tests).
- `tools/terminal_tool.py`: when delivery is unsupported, skip watcher registration, force `notify_on_complete` off, and return a `notify_unsupported` note telling the agent to `process(action='poll')`.
- `tools/delegate_tool.py`: when delivery is unsupported, fall back to **synchronous** execution (work runs and returns in the same response) with a note — strictly better than a handle that never resolves. Mirrors the existing pool-at-capacity inline fallback.

CLI (in-process `completion_queue`) and the real gateway platforms (Telegram/Discord/Slack/...) are unchanged.

## Validation
| Context | notify_on_complete | watcher registered | note |
|---|---|---|---|
| api_server | forced `False` | none | poll note |
| telegram (gateway) | `True` | yes | none |
| CLI (unbound) | `True` | none (delivers via completion_queue) | none |

E2E (real imports, temp `HERMES_HOME`, real background process) verified all three terminal contexts and the delegate sync-fallback gate. Tests: new `tests/gateway/test_async_delivery_capability.py` (10) + 463 existing tests across `tests/tools/` and `tests/gateway/` green (including the `object.__new__` bare-runner `_set_session_env` cases).

## Infographic

![honest-async-delivery](https://v3b.fal.media/files/b/0a9f37f4/5cPpgKHjLBH85YL7QIVId_3z87BJL2.png)