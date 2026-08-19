**fix: OpenClaw ports — weak credential guard + Matrix m.mentions**

## Summary
Two OpenClaw ports cherry-picked onto current main:

**1. Reject weak placeholder credentials at startup** (from #8677, )
- Extracts `_validate_gateway_config()` for testability
- Checks enabled platform tokens against `has_usable_secret()` — disables platforms with placeholder values (`***`, `changeme`, etc.) with a clear error
- Rejects placeholder `API_SERVER_KEY` when binding to network-accessible addresses

**2. Trust m.mentions.user_ids as authoritative mention signal** (from #8673, )
- Per MSC3952 / Matrix v1.7, `m.mentions.user_ids` is the spec-defined mention signal
- Clients that set m.mentions but don't duplicate @bot in body text were silently dropped
- Text-based fallback remains for older clients

## Tests
54 tests pass (test_matrix_mention.py + test_weak_credential_guard.py)

,