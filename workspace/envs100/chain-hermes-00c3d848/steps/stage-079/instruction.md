**fix(gateway,cron): close ephemeral agents + reap stale aux clients (salvage #13979)**

Salvages #13979 (@bloodcarter) — , #14210, #14368.

## Problem

macOS gateway hits `OSError: [Errno 24] Too many open files` after ~4 days and degrades across Telegram, cron, `.env` loads, dynamic imports, and outbound LLM/httpx calls. Only a gateway restart recovers.

Two root causes, both missing the existing per-turn cleanup path:

1. **Cron scheduler leaks its ephemeral `AIAgent` per tick.** `cron/scheduler.py::run_job` spawns a fresh AIAgent + `AsyncOpenAI` client inside a new `ThreadPoolExecutor` worker thread (new event loop). The `finally` block only restored `TERMINAL_CWD` and closed `SessionDB` — never called `agent.close()` and never reaped `auxiliary_client._client_cache`. Every tick leaks 1 KQUEUE fd, 2 unix socket fds (self-pipe pair), plus N httpx connection-pool fds. With macOS launchd's default `RLIMIT_NOFILE=256`, a gateway with 6 daily cron jobs hits EMFILE inside ~4 days — matching the reporter's timeline.

2. **Gateway `_cleanup_agent_resources` didn't reap the stale-loop cache.** The process-global `_client_cache` FIFO-evicts at 64 entries (PR #10470), but entries bound to a worker-thread loop that died with its `ThreadPoolExecutor` sit there until shutdown. Per-turn cleanup needs to call `cleanup_stale_async_clients()` so dead-loop entries are reaped between turns.

## Fix

**Cron FD cleanup (cron/scheduler.py, +20):** adds `agent.close()` and `cleanup_stale_async_clients()` in `run_job`'s outer `finally`, mirroring the gateway's per-turn cleanup.

**Gateway per-turn cleanup (gateway/run.py, +9):** `_cleanup_agent_resources` now calls `cleanup_stale_async_clients()` after `agent.close()`. Final-cleanup block calls `shutdown_cached_clients()` once (moved out of the `_kill_tool_subprocesses` helper so the 2× invocation from the drain-timeout path doesn't matter).

## Tests

- `tests/cron/test_scheduler.py` — success-path agent close assertion, `test_run_job_closes_agent_on_failure_to_prevent_fd_leak`, `test_run_job_reaps_stale_auxiliary_clients_per_tick`
- `tests/gateway/test_gateway_shutdown.py` — `test_cleanup_agent_resources_reaps_stale_aux_clients`, `shutdown_cached_clients` asserted on stop
- Targeted: `tests/cron/test_scheduler.py` + `tests/gateway/test_status.py` + `tests/gateway/test_gateway_shutdown.py` — **136 passed** locally (CI-parity via `scripts/run_tests.sh`).

## Salvage notes vs original #13979

- Rebased onto current `origin/main` (conflicts resolved; main had already extracted `_kill_tool_subprocesses` and landed the pid-path fix separately — PR's pid change is a no-op on current tree but left in place for intent parity).
- Moved `shutdown_cached_clients()` out of the per-phase helper so the double-call from the drain-timeout path doesn't trip test assertions (now invoked once, right after `_kill_tool_subprocesses("final-cleanup")`).
- Preserved bloodcarter authorship on both fix commits; added AUTHOR_MAP entry in a separate `chore(release):` commit.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/cron/test_scheduler.py`
- `tests/gateway/test_gateway_shutdown.py`
- `tests/gateway/test_status.py`