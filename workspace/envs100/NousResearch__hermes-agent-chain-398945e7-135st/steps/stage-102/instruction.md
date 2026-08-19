**feat(openrouter): add response caching support**

## Summary

Adds support for [OpenRouter's response caching](https://openrouter.ai/docs/guides/features/response-caching) (beta). When enabled, identical API requests return cached responses **for free** (zero billing on cache HITs), reducing both latency and cost.

Consolidates and supersedes #18921 (by @patp) and #19112 (by @Julientalbot), incorporating the best ideas from each:
- Env var overrides from #18921 (truthy parsing, `HERMES_OPENROUTER_CACHE` / `HERMES_OPENROUTER_CACHE_TTL`)
- Config.yaml integration + cache status logging (unique to this PR)

### How it works

OpenRouter caches responses at the edge keyed by API key + model + endpoint + streaming mode + SHA-256(request body). On a cache HIT, the response is replayed instantly with `usage: {prompt_tokens: 0, completion_tokens: 0}`.

This is **separate from and complementary to** Anthropic prompt caching (which we already support). The two work together — OR docs explicitly confirm this.

### Where Hermes benefits most

- **Auxiliary calls** — compression, session_search, web_extract with repeated/similar prompts
- **Cron jobs** — repeated identical prompts get free cache hits
- **Retries after errors** — same request retried = instant free cache hit
- **`/retry`** — user retrying the same turn

### Configuration

```yaml
# config.yaml (enabled by default — cache misses are free, hits save money)
openrouter:
  response_cache: true       # default: true
  response_cache_ttl: 300    # 1-86400 seconds (default: 300 = 5 min)
```

Environment variable overrides (precedence: env var > config.yaml > default):

```bash
HERMES_OPENROUTER_CACHE=true        # 1/true/yes/on to enable, 0/false/no/off to disable
HERMES_OPENROUTER_CACHE_TTL=3600    # integer seconds, 1-86400
```

### Changes

| File | What |
|------|------|
| `hermes_cli/config.py` | Add `openrouter` section to `DEFAULT_CONFIG` |
| `agent/auxiliary_client.py` | Add `build_or_headers()` — centralizes attribution + cache headers from config with env var override support |
| `run_agent.py` | Replace inline header dicts with `build_or_headers()` at init + credential swap; add `_or_cache_hits` counter initialized in `__init__`; add `_check_openrouter_cache_status()` for HIT/MISS logging |
| `cli-config.yaml.example` | Document the new config section |
| `website/docs/reference/environment-variables.md` | Document `HERMES_OPENROUTER_CACHE` and `HERMES_OPENROUTER_CACHE_TTL` |
| `tests/agent/test_openrouter_response_cache.py` | 46 tests: config headers, env var overrides (truthy/falsy/TTL boundaries), cache status counter |
| `tests/run_agent/test_provider_attribution_headers.py` | 2 integration tests for `_apply_client_headers_for_base_url()` |

### Design decisions

- **Default on** — purely beneficial (free cache hits, no behavioral change, zero cost for cache misses). Users who need fresh responses for identical inputs can set `response_cache: false` or `HERMES_OPENROUTER_CACHE=0`.
- **Env var > config.yaml precedence** — quick toggle via `HERMES_OPENROUTER_CACHE=0 hermes chat` without editing config files. Truthy parsing (`1`/`true`/`yes`/`on`) matches existing hermes conventions.
- **`build_or_headers()`** centralizes OpenRouter header construction in one function. All 5 header-injection sites now call this instead of duplicating the dict.
- **No prompt cache integrity impact** — adds a static `default_headers` entry, same mechanism as existing attribution headers.
- **Cache status logging** — reads `X-OpenRouter-Cache-Status` from streaming response headers and logs at INFO (HIT) / DEBUG (MISS).

### Test results

52 passed, 0 new failures.

, .