**feat(web): add Tavily as web search/extract/crawl backend**

## Summary

Salvage of PR #1707 by @kshitijk4poor (cherry-picked onto current main with authorship preserved).

Adds [Tavily](https://tavily.com) as a third web backend alongside Firecrawl and Parallel, using the Tavily REST API via httpx (no SDK dependency).

### What changed

- **Backend selection** via `hermes tools` — Tavily appears as a provider option, saves `web.backend: tavily` to config.yaml
- **All three tools supported** — search (`/search`), extract (`/extract`), and crawl (`/crawl`)
- **`TAVILY_API_KEY`** added to config registry, doctor, status, setup wizard
- **Fully backward compatible** — existing Firecrawl/Parallel users unaffected

### Files changed

| File | Change |
|------|--------|
| `tools/web_tools.py` | Tavily API helpers, normalizers, backend dispatch for all 3 tools |
| `hermes_cli/config.py` | TAVILY_API_KEY in OPTIONAL_ENV_VARS, doctor, set_config_value |
| `hermes_cli/tools_config.py` | Tavily provider entry with `web_backend: tavily` |
| `hermes_cli/setup.py` | Status check includes TAVILY_API_KEY |
| `hermes_cli/status.py` | Tavily in status display |
| `tests/tools/test_web_tools_tavily.py` | 15 new tests (API, normalizers, tool dispatch) |
| `tests/tools/test_web_tools_config.py` | 9 new backend selection + availability tests |
| `tests/hermes_cli/test_config.py` | 5 new config registry tests |