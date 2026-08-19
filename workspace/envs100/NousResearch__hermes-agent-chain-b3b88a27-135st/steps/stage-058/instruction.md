**fix(browser): support config-based CDP browser override**

Salvages #11802 (by @helix4u) onto current main — 21 commits behind, cherry-picked cleanly.

Makes `browser.cdp_url` in config.yaml work as a persistent fallback for CDP browser attachment. Previously only `BROWSER_CDP_URL` (env var set by `/browser connect`) was read, so users setting it in config.yaml (as the openclaw migration guide already documents) silently fell through to the local Playwright launcher.

## Changes
- `hermes_cli/config.py`: add `browser.cdp_url` to DEFAULT_CONFIG
- `tools/browser_tool.py`: `_get_cdp_override()` now checks env var first, then config
- `tests/conftest.py`: scrub `BROWSER_CDP_URL` + `CAMOFOX_URL` between tests
- `tests/tools/test_browser_cdp_override.py`: coverage for env/config precedence

## Validation
| | Result |
|---|---|
| Targeted tests | 67/67 pass |
| E2E (real imports, 7 scenarios) | env>config, config fallback, whitespace, malformed config, HTTP discovery — all pass |

.