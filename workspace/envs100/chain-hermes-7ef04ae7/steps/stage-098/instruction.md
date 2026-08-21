**fix(gateway): honor Discord connect timeout for ready wait + config.yaml surface**

## Summary
The Discord gateway no longer dies mid-startup when slash-command sync runs long, and the connect timeout is now configurable in `config.yaml` instead of only via an undocumented env var. .

## Root cause
There are TWO 30s timeouts. The outer gateway platform connect timeout was already configurable and respected, but a separate **hardcoded 30s inside `DiscordAdapter.connect()`'s ready-wait** fired first regardless. Accounts with many slash commands (#19776: 90–173 skills → ~28–31s sync) still got killed at 30s, and launchd looped the service.

## Changes
- `plugins/platforms/discord/adapter.py` (@konsisumer): `_discord_ready_timeout_seconds()` reads `HERMES_GATEWAY_PLATFORM_CONNECT_TIMEOUT` (default 30, `<=0` → wait indefinitely); the `connect()` ready-wait uses it instead of `timeout=30`.
- `hermes_cli/config.py`: add `gateway.platform_connect_timeout: 30` to `DEFAULT_CONFIG`.
- `gateway/run.py`: bridge `gateway.platform_connect_timeout` → env var at startup. Env wins if explicitly set (escape-hatch semantics, intentionally divergent from the config-authoritative `agent.*`/`display.*` bridges).
- `website/docs/reference/environment-variables.md`: document the env var + its config.yaml source.
- Tests: ready-wait honors the timeout; config supplies the env when unset; explicit env wins over config.

The sibling 30s sites were checked and left alone: the `on_message` username-resolution guard and the `tree.sync()` slash-sync timeout are different code paths, not the connect ready-wait.

## Validation
| Scenario | Before | After |
|---|---|---|
| Discord sync >30s, timeout raised to 90 | inner ready-wait kills at 30s → restart loop | ready-wait honors 90s → connects |
| `gateway.platform_connect_timeout: 90` in config | env-var-only, undocumented | bridged to env at startup |
| explicit `HERMES_GATEWAY_PLATFORM_CONNECT_TIMEOUT` env | n/a | wins over config (manual override) |

- 31/31 targeted tests pass (`test_discord_connect.py`, `test_config_env_bridge_authority.py`). ruff clean.
- E2E verified with real imports against an isolated `HERMES_HOME`: adapter timeout function + config→env bridge propagation.

Salvaged from #55847 (by @kshitijk4poor), which itself salvaged the adapter fix from #40070 (by @konsisumer). Both contributors' authorship preserved per-commit via rebase-merge.

## Infographic
![Discord connect timeout fix](https://v3b.fal.media/files/b/0aa06bc0/0eLeSBhcGy34uVD0T-R5s_SPVZvo6Z.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_config_env_bridge_authority.py`