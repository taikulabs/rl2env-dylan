**fix(memory): apply /memory approve against a fresh on-disk store when no live agent**

## Summary
`/memory approve` and `/memory approve all` now work from contexts with no live agent — the Hermes Desktop GUI, the TUI, and any CLI path — instead of failing with `memory store unavailable` and applying nothing. The shared on-disk fallback now also honors the user's configured memory char limits on every surface.

Root cause: `_handle_memory_command` resolved the store as `self.agent._memory_store`, which is `None` when there is no live agent, and passed it to the shared `handle_pending_subcommand`, which bails out (`if memory_store is None: return False, "memory store unavailable"`). The messaging-gateway handler already sidesteps this by applying against a freshly loaded on-disk store; the CLI/Desktop path did not.

## Changes
**Commit 1 (@maxmilian, #46926 salvage):** when the agent store is `None`, fall back to a fresh on-disk store before running the shared approval handler — mirroring the gateway. Persists to the same `MEMORY.md`/`USER.md`; creates `MEMORY.md` on the first approved write. Adds a red→green regression test.

**Commit 2 (follow-up):** both the CLI fallback and the gateway handler built a bare `MemoryStore()` with the hardcoded default char limits (2200/1375), ignoring the user's configured `memory.memory_char_limit` / `user_char_limit` (a live agent honors them — `agent/agent_init.py`). Extracted a shared `tools.memory_tool.load_on_disk_store()` factory that reads the configured limits (falling back to defaults if config can't load) and wired **both** the CLI and gateway handlers to it — closing the gap on both surfaces and de-duplicating the construction block.

## Validation
| | Before | After |
|---|---|---|
| `/memory approve all` (no live agent) | `memory store unavailable`, nothing applied | `Approved 1`, write persists to `MEMORY.md` |
| no-agent approval char caps | hardcoded 2200/1375, ignored user config | honors `memory.*_char_limit` (CLI + gateway) |

- `scripts/run_tests.sh tests/tools/test_write_approval.py` → 27/27 passing (+2 new).
- `tests/gateway/test_slash_access_dispatch.py` → 18/18.
- E2E with real imports: no-agent `/memory approve all` applies and persists; `load_on_disk_store()` picks up configured limits (900/300 from a real config.yaml).

## Credit
Salvage of #46926 by @maxmilian (

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_write_approval.py`