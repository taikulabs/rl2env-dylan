**fix(weixin,api_server): proxy support, content normalization, HermesClaw docs**

## Summary

Three changes salvaged from community PRs, each independent and clean.

### 1. Proxy support for aiohttp sessions (
Adds `trust_env=True` to all `aiohttp.ClientSession()` calls in weixin.py, wecom.py, and matrix.py. This makes aiohttp respect `HTTP_PROXY`/`HTTPS_PROXY` env vars — critical for Chinese users behind proxies (Clash fake-IP mode) who can't connect to WeChat/WeCom APIs at all without it. No-op for non-proxy users.

**Author:** Sicheng Li (@MaybeRichard)

### 2. HermesClaw community docs (
One-line README addition linking HermesClaw (community WeChat bridge) in the Community section.

**Author:** AaronWong1999 (@AaronWong1999)

### 3. Normalize array-based content parts in API server (salvaged from #7980)
Some OpenAI-compatible clients send content as typed arrays (`[{type: 'text', text: 'hello'}]`) instead of strings. The Chat Completions endpoint had no normalization, causing silent failures. Adds `_normalize_chat_content()` with defensive limits (recursion depth, list size, 64KB output cap) and applies it to both Chat Completions and Responses API endpoints. The Responses path had inline normalization that only handled `input_text`/`output_text` — the shared function also handles the standard `text` type.

**Only the content normalization from #7980 was taken.** The SSE changes (reverted #6972 tool progress fix, removed keepalive pings) and Weixin changes (conflicted with #8665, removed retry logic, removed blank-message guards) were regressions and are excluded.

**Author:** ikelvingo (@ikelvingo) — co-authored

## Files changed
- `gateway/platforms/weixin.py` — trust_env=True (3 locations)
- `gateway/platforms/wecom.py` — trust_env=True (1 location)
- `gateway/platforms/matrix.py` — trust_env=True (1 location)
- `gateway/platforms/api_server.py` — _normalize_chat_content function + applied in 2 endpoints
- `tests/gateway/test_api_server_normalize.py` — 17 new tests
- `README.md` — 1 line added