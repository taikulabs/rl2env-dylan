**fix(hindsight): flush buffered turns + drop stale prefetch on session switch**

Salvage of #17447 (@nicoloboschi) — same fix, same tests, + one follow-up: route the flush through the existing writer queue instead of a raw thread.

## Summary
`HindsightMemoryProvider.on_session_switch` was silently losing partial batches and leaking prior-session recall across `/reset`, `/resume`, `/branch`, `/new`, and context compression. This PR flushes buffered turns under the OLD `document_id` with OLD lineage before rotation, drains in-flight prefetch, and clears `_prefetch_result`.

## Bugs fixed (from #17447)
1. **Data loss when `retain_every_n_turns > 1`** — `on_session_switch` cleared `_session_turns` without flushing. Any in-flight batch disappeared at session switch time. Same data-loss class as the shutdown race, different lifecycle event. Reproduced on current main via bare-object repro: `_session_turns=['a','b']` → `on_session_switch('new')` → buffer is `[]` with zero flush.
2. **Stale prefetch leak across switch** — if `queue_prefetch` ran in the old session and `prefetch()` hadn't consumed the result, the new session's first `prefetch()` returned text mined from the prior session's bank.

## Follow-up in this salvage (second commit)
Nicolò's original fix spawned a raw `threading.Thread` for the flush, overwriting `self._sync_thread` (which is aliased to the long-lived writer thread). Two issues:

1. **No serialization with the writer queue.** `sync_turn` enqueues retains on `_retain_queue` drained by the long-lived `_writer_thread`. The raw-thread flush ran concurrently with the writer — two threads could call `aretain_batch` against the same `document_id`.
2. **Broken pre-spawn join.** The `self._sync_thread.join(timeout=5.0)` before spawn tried to join the long-lived writer, which never exits on its own, so it always timed out and never actually serialized anything.

Fix: enqueue the flush closure on `_retain_queue` via `_ensure_writer()` + `put()`, the same path `sync_turn` uses. Natural FIFO ordering behind any pending retains, no new thread, no broken join. Shutdown-aware (`if not self._shutting_down.is_set()`) so it can't enqueue during teardown.

## Tests
- 4 tests from Nicolò — buffer flushed under OLD doc/lineage, no spurious retain on empty buffer, `_prefetch_result` cleared, in-flight prefetch drained.
- 1 new regression guard — `test_flush_serializes_behind_pending_retains_via_writer_queue` blocks the writer mid-retain with an Event and proves the flush lands FIFO behind the pending retain rather than racing it.
- **103/103 passing** on `tests/plugins/memory/test_hindsight_provider.py` + `tests/agent/test_memory_session_switch.py`.
- E2E against the worktree: bare-object repro against patched code → flush enqueued on writer queue with OLD `document_id` and `session:old` lineage tag; stale prefetch cleared; rotation completes.

## Commits
- `c3bbdc23d` — original fix (authored by @nicoloboschi, cherry-picked)
- `177a6905e` — follow-up: route flush through writer queue

.