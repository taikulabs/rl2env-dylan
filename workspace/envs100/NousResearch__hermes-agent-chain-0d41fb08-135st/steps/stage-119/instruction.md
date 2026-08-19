**feat(gateway): add WeCom callback-mode adapter for self-built apps**

## Summary

Adds WeCom callback-mode as a dedicated platform (`Platform.WECOM_CALLBACK`) for regular enterprise self-built applications. Completely separate from the existing bot-mode `Platform.WECOM` — both can run simultaneously.

### Architecture

1. WeCom POSTs encrypted XML → adapter decrypts → queues message for agent
2. Immediately acknowledges with plain `"success"` (silent ack, nothing displayed)
3. Agent processes for 3-30 minutes
4. Reply delivered proactively via `message/send` API with access-token

**Key simplification from original PR:** Removed the Future/pending-reply system that held the HTTP response open for 4.5s — agent sessions take 3-30 minutes, so inline reply is never useful. Immediate ack + proactive send only.

### Platform isolation

Uses `Platform.WECOM_CALLBACK` (not `Platform.WECOM`). No config-based routing ambiguity — they're separate platform entries that can coexist. Bot mode and callback mode can run in the same gateway instance.

### Features
- AES-CBC encrypt/decrypt (BizMsgCrypt-compatible) via `wecom_crypto.py`
- Multi-app routing scoped by `corp_id:user_id` — prevents cross-corp collisions
- Legacy bare `user_id` fallback for backward compat
- Access-token management with auto-refresh (7200s TTL)
- `WECOM_CALLBACK_*` env var overrides
- Port-in-use pre-check before binding
- Health endpoint at `/health`

### Files changed (+752/-2)
- `gateway/platforms/wecom_callback.py` — **new** callback adapter (387 lines)
- `gateway/platforms/wecom_crypto.py` — **new** WXBizMsgCrypt crypto (142 lines)
- `tests/gateway/test_wecom_callback.py` — **new** 9 tests
- `gateway/config.py` — `Platform.WECOM_CALLBACK` enum; recognize callback configs; env overrides
- `gateway/run.py` — dedicated `elif Platform.WECOM_CALLBACK` branch; allowlist/allow-all maps; update-allowed set
- `tools/send_message_tool.py` — `wecom_callback` platform target

### Test results
57/57 gateway tests pass (callback + wecom + config)

Salvaged from PR #7774 by @chqchshj. Contributor authorship preserved.