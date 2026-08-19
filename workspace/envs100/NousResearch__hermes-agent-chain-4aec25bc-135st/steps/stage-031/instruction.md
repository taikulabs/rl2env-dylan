**fix(run_agent): isolate background review fork from external memory plugins**

## Summary
Background memory/skill review forks no longer leak harness prompts into external memory plugin namespaces (honcho, mem0, supermemory, etc.).

Reported by @Utku — the review harness prompts (`Review the conversation above and update the skill library...`) were getting ingested by memory plugins as if they were real user conversation.

## Root cause
`_spawn_background_review()` creates a fresh `AIAgent` to do the review. That `__init__` rebuilds its own `_memory_manager` from `memory.provider` in config, scoped to the parent's `session_id`. Then `run_conversation()` triggers three ingestion sites against the user's real memory namespace:

| Site | What gets written |
|---|---|
| `on_turn_start(turn_count, prompt)` | harness prompt as the turn's user message; advances cadence |
| `prefetch_all(prompt)` | harness prompt as a recall query |
| `sync_all(prompt, review_output, session_id)` | harness prompt + review output as a `(user, assistant)` pair |

## Changes
- `run_agent.py` `_spawn_background_review()` — pass `skip_memory=True` to the fork's `AIAgent(...)` constructor
- `tests/run_agent/test_background_review.py` — regression test asserting the kwarg is set

## Why this works
`skip_memory=True` short-circuits both `_memory_store` and `_memory_manager` construction in `__init__`. The existing fork-setup block at L4310-4314 explicitly rebinds `_memory_store`, `_memory_enabled`, `_user_profile_enabled`, and the nudge intervals from the parent right after construction — so:

- Built-in `MEMORY.md` / `USER.md` writes via the `memory` tool still land on disk ✓
- Skill writes still work (skills don't go through MemoryManager at all) ✓
- All three ingestion sites short-circuit on `if self._memory_manager:` ✓
- `shutdown_memory_provider()` on the fork becomes a no-op (nothing to shut down) ✓
- Cached system prompt is still inherited verbatim from parent (prefix cache parity preserved) ✓

## Validation
| | Before | After |
|---|---|---|
| Fork `_memory_manager` (with honcho configured) | non-None, providers=['honcho'] | None |
| Fork `_memory_store` after rebinding | parent's store object | parent's store object (identity preserved) |
| Fork `_memory_enabled` after rebinding | True | True |
| `on_turn_start` / `prefetch_all` / `sync_all` gates | all evaluated | all short-circuit |
| Targeted background-review tests | 28/28 pass | 28/28 pass |

E2E verified with a stubbed honcho provider in an isolated `HERMES_HOME`: with `skip_memory=True` the fork constructs with `_memory_manager=None` even though `memory.provider=honcho` is set in config; without it, the fork builds a manager wired to the stub.