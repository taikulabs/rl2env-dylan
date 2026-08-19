**feat(x_search): auto-enable toolset when xAI credentials are configured**

## Summary
The `x_search` toolset now auto-enables when the user has xAI Grok OAuth tokens (SuperGrok subscription) OR `XAI_API_KEY` set — matching the original intent. Previously users had to also click through `hermes tools` → X (Twitter) Search even though they already had working credentials.

## Why a separate code path from `HASS_TOKEN` → `homeassistant`
`ha_*` tools live inside the `hermes-cli` composite, so the subset-inference loop picks them up and the HASS branch just unmasks `default_off`. `x_search` is its own one-tool toolset NOT in the composite, so the subset loop never adds it — it has to be injected directly, with a parallel `default_off` carve-out.

## Changes
- `hermes_cli/tools_config.py`:
  - New `_xai_credentials_present()` — side-effect-free check for stored xAI OAuth tokens or `XAI_API_KEY` (dotenv or env). No network.
  - In `_get_platform_tools()` else branch (no explicit user config saved), inject `x_search` and carve a parallel hole in `default_off`.
- `tests/hermes_cli/test_tools_config.py`: 4 new tests.

## Behavior
| Scenario | Result |
|---|---|
| xAI OAuth tokens stored, no saved config | `x_search` auto-enabled (cli, cron, telegram) |
| `XAI_API_KEY` set, no saved config | `x_search` auto-enabled |
| No xAI credentials | `x_search` off (unchanged) |
| User saved explicit config without `x_search` | `x_search` off (saved list authoritative) |
| `agent.disabled_toolsets: [x_search]` | `x_search` off (global override wins) |

## Validation
- `scripts/run_tests.sh tests/hermes_cli/test_tools_config.py` → 70/70 passing
- `scripts/run_tests.sh tests/tools/test_x_search_tool.py tests/hermes_cli/test_auth_xai_oauth_provider.py` → 76/76 passing
- E2E run with isolated `HERMES_HOME` confirmed all 5 behavior rows above