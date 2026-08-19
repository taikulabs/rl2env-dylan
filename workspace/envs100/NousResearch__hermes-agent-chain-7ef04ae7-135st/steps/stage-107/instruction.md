**fix(profile): prevent profile context loss in desktop + multiplexed gateway**

## Summary
Profiles served from a single process (desktop `tui_gateway`, `gateway.multiplex_profiles`) no longer leak one profile's reads/writes into another. These topologies switch profile via a context-local override, not the process env — anything that resolved the profile outside that request context reverted to the launch profile.

Root cause is a two-part bug class: (1) import-time / process-global path state pinned to the first profile that imported it, and (2) worker threads that start with an empty context and never inherit the override.

## Changes
- **Per-call path resolution** — `tools/skills_hub.py` (resolvers + PEP 562 `__getattr__` to keep the old constant names and the `patch.object` test seam), `gateway/platforms/base.py` cache-dir getters, `gateway/rich_sent_store.py` (`get_hermes_home()` not `os.environ`), `plugins/platforms/whatsapp/adapter.py` media validator.
- **Thread context propagation** — wrap the three leaking spawns in the existing `propagate_context_to_thread`: the `model_tools.py` sync→async tool worker, the `run_agent.py` background-review thread, and both `tools/async_delegation.py` submits.
- **Background-review memory gating** — `agent/background_review.py` gates the built-in `memory` tool on `_memory_enabled` / `_user_profile_enabled` instead of a hardcoded `["memory", "skills"]`, so a `memory_enabled: false` profile no longer gets the MEMORY.md tool (#54937 layer 2).
- 4 new test files (28 tests): two-profile runtime suite, the real multiplexed-gateway scope, the WhatsApp media validator, and the bg-review toolset restriction.

## Validation
| | Before | After |
|---|---|---|
| Profile-scoped paths in multiplexed/desktop runtime | revert to launch profile | follow active override |
| Worker-thread tool dispatch | empty context → launch profile | inherits override |
| bg-review on `memory_enabled: false` profile | gets MEMORY.md tool | tool gated out |
| Targeted tests | — | 28/28 passing |

. Supersedes #54948 (that PR snapshots `_mem_dir` at `MemoryStore.__init__`; this keeps the per-call resolution main already has, which is correct under mid-process switches). Honcho client singleton + MCP registry are a separate caching-lifetime boundary, tracked as follow-up.

Salvage of #55867 by @erosika (Eri Barrett) — cherry-picked onto current `main` with authorship preserved.

## Infographic
![Profile Context Isolation](https://v3b.fal.media/files/b/0aa06be5/ESu84B8PsZJJPOAZ8G2Mn_D04PYjQL.png)