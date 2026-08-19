**fix(gateway): coerce plaintext "restart gateway" DMs to /restart**

Rewrite plaintext `restart gateway` / `restart the gateway` / `restart hermes` DMs to `/restart` before they reach the agent loop.

## Why
Without the shortcut, "restart gateway" can land in the LLM as a user turn. The agent tries to satisfy it via `terminal(systemctl restart ...)`, which kills the gateway mid-run. The old process gets stuck in `draining` state while systemd waits on the process it's about to kill — classic self-kill deadlock.

The slash-command path uses `request_restart(...)` which drains cleanly.

## Scope (intentionally narrow)
- DM text messages only — group chats keep natural-language semantics
- Exact restart-style phrases only (compiled regexes)
- No-op if the text already starts with `/`

## Changes
- `gateway/platforms/base.py`
  - New `coerce_plaintext_gateway_command(event)` helper with 3 regexes.
  - Called once in `BasePlatformAdapter.handle_message` — covers every platform and the pending-message reinjection path.
- `tests/e2e/conftest.py`: thread `chat_type` through `make_source` / `make_event` so tests can exercise group chats.
- `tests/e2e/test_platform_commands.py`: 2 new Telegram-parametrized tests.
  - DM `restart gateway` → `runner.request_restart(detached=False, via_service=True)`.
  - Group chat `restart gateway` → falls through to normal agent path.

## Validation
`scripts/run_tests.sh tests/e2e/test_platform_commands.py` → 47 passed, 4 skipped (non-Telegram skips by design).

## Credit
Salvaged from #16863 by @beesrsj2500. Original PR bundled four unrelated changes; this PR is the plaintext-coercion portion only. Simplified from the original by removing a duplicate runner-level call — the adapter-level call covers all code paths.