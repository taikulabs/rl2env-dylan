**fix(nous): keep Nous auth fresh for idle dashboard/gateway agents**

## Summary
Hosted Nous agents now keep their Portal/pool auth fresh while the dashboard or gateway process is up, so an idle agent no longer hits expired invoke JWTs on its next action.

## Root cause
Nous has refresh-token support, but the dashboard/gateway only refreshed reactively on a request path. If an agent sat idle long enough, nothing refreshed the Portal/session state, so the next dashboard/gateway action could see stale invoke credentials and leave the user in a bad launch/login state.

## Changes
- `hermes_cli/nous_auth_keepalive.py` (new): daemon keepalive thread (6h interval, 60s initial delay) that refreshes the selected Nous credential-pool entry, falling back to singleton auth refresh. Started in `gateway/run.py` and `web_server.start_server`, stopped on graceful shutdown.
- `hermes_cli/runtime_provider.py`: when the selected Nous pool entry's invoke JWT is stale/missing, refresh it in place via `pool.try_refresh_current()` before falling through to singleton resolution (previously just cleared `pool_api_key`).
- `agent/auxiliary_client.py`: auxiliary Nous resolution refreshes stale pool entries instead of trying expired invoke JWTs; singleton auth refresh remains the fallback.
- `tests/run_agent/test_provider_parity.py`: autouse fixture resets aux provider health state so rate-limit sims don't leak across tests.
- Reuses existing internal env vars (`HERMES_NOUS_MIN_KEY_TTL_SECONDS`, `HERMES_NOUS_TIMEOUT_SECONDS`) — no new user-facing config.

## Validation
| | Result |
|---|---|
| `py_compile` (5 modified modules) | OK |
| `test_nous_auth_keepalive` + `test_runtime_provider_resolution` + `test_auxiliary_client` + `test_provider_parity` | 450 passed |

Salvage of #48131 (@shannonsands) cherry-picked onto current main, authorship preserved. Linear: NS-539.

## Infographic

![nous-auth-keepalive](https://v3b.fal.media/files/b/0a9f448b/kOQ8gfvSRtNBnJ0psJHV4_PSS3qS9k.png)