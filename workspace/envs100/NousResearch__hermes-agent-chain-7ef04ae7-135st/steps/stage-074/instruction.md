**fix(credentials): prefer ~/.hermes/.env over stale os.environ on key rotation**

## Summary
A rotated API key in `~/.hermes/.env` now wins over a stale value still exported in the parent shell, closing the remaining path that produced persistent 401s after key rotation.

## Background
#20591 was closed as fixed, but only the **credential-pool seeding** path was corrected (#18254/#18755). The **live request-time resolution** path was still broken: `_resolve_api_key_provider_secret` (`hermes_cli/auth.py`) resolved keys via `get_env_value()`, which returns the `os.environ` value first. So after a `.env` rotation, the pool re-seeded with the fresh key while the resolution path kept returning the stale shell export → 401s on every request.

Verified live on current `main` before this fix:
```
_resolve_api_key_provider_secret("deepseek") -> sk-STALE-from-shell   (stale wins — bug)
```

## Changes
- `hermes_cli/config.py`: add `get_env_value_prefer_dotenv()` — checks `~/.hermes/.env` first, then `os.environ`. **Distinct** from `get_env_value()` (unchanged, os.environ-first) so only Hermes-managed credential resolution flips precedence; the generic helper's many other callers are unaffected.
- `hermes_cli/auth.py`: `_resolve_api_key_provider_secret` resolves through the new helper.
- `tests/`: regression coverage for **both** the pool-seeding path and the auth-resolution path (a rotated `.env` key must beat a stale shell export).

## Validation
| | Before | After |
|---|---|---|
| `_resolve_api_key_provider_secret` (rotated .env, stale shell) | stale shell key | rotated `.env` key |
| `get_env_value()` (generic helper) | os.environ-first | os.environ-first (unchanged) |

- 91 tests pass across `tests/tools/test_credential_pool_env_fallback.py` + `tests/agent/test_credential_pool.py` (89 prior + 2 new regressions); ruff clean.
- E2E against a real resolution path (isolated `HERMES_HOME`, `.env` vs `os.environ`): the rotated key now wins, with a negative control confirming `get_env_value()` is unchanged (no blast-radius regression).

## Credit
Salvage of #20602 by @0xDevNinja, who located the exact still-broken path (`_resolve_api_key_provider_secret` → `get_env_value`) that the earlier pool-only fix didn't cover. Cherry-picked to preserve authorship; rebased onto current `main` (the original was ~5.5k commits behind). The PR's `credential_pool.py` change was dropped — that path already prefers `.env` on current `main` (via `secret_scope`), so the substantive fix is `config.py` + `auth.py` only.

.