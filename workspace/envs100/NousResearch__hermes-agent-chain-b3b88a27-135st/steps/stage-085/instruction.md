**fix(honcho): dialectic lifecycle, gateway scoping, provider opt-in**

## Summary

Salvage of #12160 (Erosika) + #12318 (helix4u) + 

### What this PR does

**Honcho dialectic lifecycle fixes (PR #12160 by @erosika, 

Chain of correctness and reliability fixes on the Honcho dialectic path:

- **Prewarm consumption fix** — session-start `prefetch_dialectic()` wrote to `_dialectic_cache` but `pop_dialectic_result()` had zero call sites. Prewarm now writes directly to `_prefetch_result` so turn 1 consumes it without a duplicate `.chat()` call. Dead code purged (`prefetch_dialectic`, `_dialectic_cache`, `set_dialectic_result`, `pop_dialectic_result`).
- **Cadence advances only on success** — `_last_dialectic_turn` now moves only when the result is non-empty, so empty returns (transient API error, sparse representation) retry on the next eligible turn instead of burning the cadence window.
- **Gateway user_id scoping** (@LeonSGP43, #11434) — gateway `user_id` no longer mutates `cfg.peer_name`. Threaded as `runtime_user_peer_name` through `HonchoSessionManager`, preferred in `get_or_create()`. .
- **Stale-thread watchdog** — prefetch thread older than `timeout × 2` treated as dead so a hung Honcho call can't block future fires.
- **Stale-result discard** — pending result older than `cadence × 2` turns is dropped on read.
- **Empty-streak backoff** — consecutive empty returns widen effective cadence (`cadence + streak`, capped at `cadence × 8`).
- **Trivial prompt skip** — "ok", "y", "thanks", slash commands short-circuit both injection and dialectic.
- **Query-length reasoning heuristic** (restored) — scales `dialecticReasoningLevel` by query length (+1 at ≥120 chars, +2 at ≥400), clamped at `reasoningLevelCap`.
- **Setup wizard** — adds reasoning-level step, cadence default updated to 2.
- **Docs** — session-start prewarm, observation reference, multi-peer setup, query-adaptive reasoning.

**Honcho provider opt-in fix (PR #12318 by @helix4u):**

Removes the Honcho auto-migration block from `AIAgent.__init__()`. A blank `memory.provider` now stays opt-in — stale `HONCHO_API_KEY` / `HONCHO_BASE_URL` in `.env` no longer rewrites `memory.provider: honcho` back into config after the user has removed it. The migration served its purpose (March 2026 plugin transition) and is no longer needed.

### Follow-up commit

- `chore: add LeonSGP43 numeric noreply email to AUTHOR_MAP` — the +LeonSGP43@users.noreply.github.com` which wasn't in the map.

## Test results

```
298 passed, 3 skipped (tests/honcho_plugin/ + tests/agent/test_memory_*.py + tests/run_agent/test_memory_provider_init.py)
```

## Credits

- @erosika — 6 commits (dialectic lifecycle, liveness, heuristic, docs, wizard)
- @LeonSGP43 — 1 commit (gateway user_id scoping, 
- @helix4u — 1 commit (Honcho provider opt-in fix, 

Supersedes #12160, #12318, #11434.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/run_agent/test_memory_provider_init.py`