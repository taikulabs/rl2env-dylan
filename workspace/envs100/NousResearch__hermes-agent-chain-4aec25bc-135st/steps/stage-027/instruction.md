**fix(agent): reset _fallback_index at turn start even when no fallback activated**

Salvage of #20793 onto current main. Preserves @konsisumer's authorship.

## Summary
Interactive CLI sessions now honor `fallback_providers` on Codex 429 `usage_limit_reached` (and all other failures), matching cron behavior.

Root cause: `_try_activate_fallback()` increments `_fallback_index` BEFORE resolving the provider's client. When every chain entry's resolver returns `None` (or raises), the recursive walk exhausts `_fallback_index` to `>= len(_fallback_chain)` but never sets `_fallback_activated = True`. Next turn, `_restore_primary_runtime()` early-returns because `_fallback_activated` is False, so the chain index stays exhausted forever. The eager-fallback check at the top of the retry loop sees the exhausted index and silently skips — no "trying fallback" log line, no status message, just 3 retries and "API call failed after 3 retries."

Cron jobs work because each cron run constructs a fresh `AIAgent` with `_fallback_index = 0`.

## Changes
- `run_agent.py`: add `self._fallback_index = 0` in the `not _fallback_activated` early-return branch of `_restore_primary_runtime()`.
- `tests/run_agent/test_primary_runtime_restore.py`: regression test exercising the failed-activation path.

## Validation
- `scripts/run_tests.sh tests/run_agent/test_primary_runtime_restore.py tests/run_agent/test_provider_fallback.py -q` → 54/54 passed.

. Original PR #20793.