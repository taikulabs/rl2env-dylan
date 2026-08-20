**fix(telegram): wire keepalive limits into general request pool to fix CLOSE_WAIT fd leak**

## Summary

 — the Telegram adapter leaks httpx **general-pool** connections (CLOSE_WAIT fd leak), notably through an HTTP proxy.

The general request pool (`_request[1]`, which routes `bot.send_message` / `set_my_commands`) is built from `HTTPXRequest(...)` with `connection_pool_size` / `pool_timeout` / timeouts but **no httpx keepalive tuning**, so httpx's default `keepalive_expiry=5.0` lets dead sockets linger in CLOSE_WAIT. `_drain_polling_connections()` only resets `_request[0]` (the polling pool) and deliberately leaves `_request[1]` untouched — so the general pool has no recycling path. Telegram was the **lone holdout** of the #18451 CLOSE_WAIT class: wecom/dingtalk/signal/whatsapp/bluebubbles/qqbot already route through the shared `platform_httpx_limits()` helper; Telegram did not.

Verified still live on current `main` (`plugins/platforms/telegram/adapter.py`): no `limits` / `keepalive_expiry` / `max_keepalive_connections` on the general-pool construction; `platform_httpx_limits()` not wired in.

## Fix

Wire the shared `gateway/platforms/_http_client_limits.py::platform_httpx_limits()` (bounded `max_keepalive_connections` + sub-default `keepalive_expiry`) into the general-pool `HTTPXRequest` construction across **all three branches** — fallback-transport, **proxy** (the reporter's actual path), and plain — via `httpx_kwargs={"limits": ...}`. PTB spreads `httpx_kwargs` last into its client kwargs, so this cleanly overrides PTB's default limits while preserving `max_connections=connection_pool_size`.

## Why not PR #49930

The existing candidate #49930 was not salvageable:
- it defines `_TCP_KEEPIDLE`/`TCP_KEEPINTVL`/`TCP_KEEPCNT` (Linux-only) at module top with **no `hasattr` guard** → **crashes on import on macOS** (the reporter's own OS);
- it patches `TelegramFallbackTransport`, which the **proxy** repro never instantiates → doesn't fix the reported path.

This PR takes the proven keepalive-limits vector via the existing helper (no Linux-only socket constants → macOS-import-safe) and covers the proxy branch the reporter hit. Co-authored credit to @indigokarasu for the report + diagnosis.

## Tests

`tests/gateway/test_telegram_closewait_limits_31599.py` — drives `connect()` across the **proxy** and **plain** branches with a recording `HTTPXRequest`, asserts each gets `httpx_kwargs["limits"]` = `httpx.Limits` with `keepalive_expiry < 5.0`, bounded `max_keepalive_connections`, and preserved `max_connections`. 56 pass (new tests + `test_platform_http_client_limits.py` + `test_telegram_network.py`); mutation-checked (dropping the limits wiring fails both branch tests). `import plugins.platforms.telegram.adapter` confirmed clean on macOS.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_telegram_closewait_limits_31599.py`