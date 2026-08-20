**fix(telegram): honor proxy env vars in fallback transport (salvage #3411)**

## Summary
Salvage of #3411 by kufufu9. Cherry-picked onto current main with authorship preserved.

Makes `TelegramFallbackTransport` read standard proxy env vars (`HTTPS_PROXY`, `HTTP_PROXY`, `ALL_PROXY`) and pass them to the underlying `httpx.AsyncHTTPTransport` instances. Without this, users behind corporate proxies can't reach Telegram through our custom transport — httpx only auto-resolves proxy env vars at the `AsyncClient` level, not the transport level.

No-op when proxy env vars aren't set.

## Changes
- New `_resolve_proxy_url()` helper reads proxy env vars in standard precedence order
- Injects `proxy=url` into transport kwargs (respects explicit caller overrides)
- Test verifies both primary and fallback transports receive the proxy

## Credit
Original work by @kufufu9 in #3411.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_telegram_network.py`