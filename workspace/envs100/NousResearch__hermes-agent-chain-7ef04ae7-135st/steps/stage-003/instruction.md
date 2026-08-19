**fix(kanban): retry write_txn on transient SQLITE_BUSY**

## Summary

Concurrent kanban writers on a shared `kanban.db` no longer hard-fail with `database is locked` — transient `SQLITE_BUSY` is now absorbed by a bounded jittered retry instead of surfacing as an error to the losing writer.

Root cause: `write_txn` opened and committed an `IMMEDIATE` transaction with no application-level retry. SQLite's own `busy_timeout` backs off near-deterministically, so contending writers re-collide in lockstep (a convoy) rather than spreading out — that convoy is what surfaces the lock error under a stampede.

The fix adds a bounded jittered retry on the transaction boundary only. `BEGIN IMMEDIATE` and `COMMIT` are idempotent re-issues that touch no transaction body, so a claim CAS inside `write_txn` is never replayed and a non-busy error is never retried. `busy_timeout` is unchanged.

## Changes

- `hermes_cli/kanban_db.py`: `_execute_boundary_with_retry()` wraps `BEGIN IMMEDIATE` / `COMMIT` with 5 retries on a 20–150ms jitter band (20ms floor prevents busy-spinning back into the collision). Ports state.db's `_execute_write` pattern (retries trimmed 15→5, justified by kanban's 120s `busy_timeout`). COMMIT exhaustion rolls back so the connection isn't poisoned for the next `BEGIN IMMEDIATE`.
- `tests/hermes_cli/test_kanban_write_txn_busy_retry.py`: 8 boundary tests covering transient + persistent BUSY at both BEGIN and COMMIT, the jitter floor, body-not-replayed, and rollback on exhausted COMMIT.

## Validation

| | Result |
|---|---|
| New boundary tests | 8 pass; **5 fail on unmodified main** (verified) |
| Premise | state.db `_execute_write` uses the same 20–150ms jitter band — faithful port |
| Scope | migration-path `BEGIN IMMEDIATE` left untouched (runs under init locks, no contention) |
| Stampede (contributor) | 24 concurrent writers, 0 failures at shipped 120s `busy_timeout` + 5 retries |

## Credit

## Infographic

![kanban-write-retry](https://v3b.fal.media/files/b/0aa0174e/TlRmL1V2LApX2810qzNfe_FK1lOB5g.png)