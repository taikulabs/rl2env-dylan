**feat(browser): add browser_cdp raw DevTools Protocol passthrough**

Agents now have a raw CDP escape hatch for browser operations not covered by the existing browser tools — dialog handling, iframe-scoped evaluation, cookie/network control, and any other CDP verb. **Gated on a reachable CDP endpoint at session start** — the tool only appears in the toolset when `/browser connect` is active or `browser.cdp_url` is set.

## Changes
- `tools/browser_cdp_tool.py` (new, ~300 lines): registers `browser_cdp(method, params, target_id, timeout)`. Opens a fresh WebSocket per call; for page-level methods it calls `Target.attachToTarget` with `flatten=true` and dispatches using the returned `sessionId`. Browser-level methods (`Target.*`, `Browser.*`, `Storage.*`) skip attachment.
- `_browser_cdp_check()` gates the tool: returns True only when browser requirements are met AND `_get_cdp_override()` returns a URL. Tool is hidden from the model otherwise — no tool bloat on backends that can't use it.
- Schema description embeds the CDP reference URL (https://chromedevtools.github.io/devtools-protocol/) so the agent can `web_extract` specific method docs on demand.
- `toolsets.py`: `browser_cdp` added to `_HERMES_CORE_TOOLS`, `browser`, `hermes-acp`, and `hermes-api-server` toolsets.
- Docs: new `browser_cdp` section in `user-guide/features/browser.md`, table entries in `reference/tools-reference.md` (count bumped 52 → 53) and `reference/toolsets-reference.md`, all clarifying the gating.

## Backend availability (verified)

| Backend | Tool visible? |
|---|---|
| `/browser connect` (BROWSER_CDP_URL) | yes |
| `browser.cdp_url` in config.yaml | yes |
| agent-browser default local (no connect) | no — Playwright's internal CDP port isn't exposed |
| Browserbase / Browser Use / Firecrawl cloud | no — per-session `cdp_url` exists but isn't surfaced yet (follow-up) |
| Camofox | no — REST-only, never supports CDP |

## Validation

| Check | Result |
|---|---|
| `py_compile` on all touched modules | ok |
| `scripts/run_tests.sh tests/tools/test_browser_cdp_tool.py tests/test_toolsets.py` | 43 passed |
| E2E against real headless Chrome (7 cases: Target.getTargets, Browser.getVersion, Runtime.evaluate with target_id, Page.navigate + re-eval title, bogus method, bogus target_id, no-endpoint error) | 7/7 pass |
| E2E of the gate (tool hidden without CDP URL, visible with it, hidden again after unset) | pass |
| `ascii-guard lint` on changed docs | clean |

Unit tests use a tiny in-process `websockets` server to exercise the real protocol (connect, attach, dispatch, error, timeout) without needing Chrome. Three new tests cover the `check_fn` gate — verifying it returns False without a CDP URL, True with one, and False when browser requirements overall fail.

## Notes
Stateless by design: each call opens and closes its own WS. Sessions and event subscriptions do not persist between calls — the schema description says so explicitly. Stateful flows (e.g. dialog-event subscription) are a follow-up, which is what step #2 (dialog handling) will address.

Cloud-provider CDP routing is also follow-up work — Browserbase/Browser Use/Firecrawl all return a `cdp_url` in their `create_session()` response per the base class contract, but we don't surface that live yet.

Part 1 of 3 from the browser-harness capability mirror thread — #2 is dialog handling, #3 is domain-skill auto-surfacing on `browser_navigate`.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_browser_cdp_tool.py`