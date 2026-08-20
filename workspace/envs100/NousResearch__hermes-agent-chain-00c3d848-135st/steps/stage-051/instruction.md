**fix(gateway): enforce max_size in MessageDeduplicator for fresh entries**

Salvage of #15913 onto current main. Authorship preserved.

## Summary
Caps `MessageDeduplicator._seen` at `max_size` even when every entry is still inside the TTL window. Previously, overflow handling only dropped TTL-expired entries, so under sustained traffic the cache grew unbounded.

## Changes
- `gateway/platforms/helpers.py`: after TTL pruning on overflow, keep the newest `max_size` entries by timestamp.
- `tests/gateway/test_message_deduplicator.py`: regression test with all-fresh entries.

## Validation
`scripts/run_tests.sh tests/gateway/test_message_deduplicator.py` — 8/8 passing.

.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_message_deduplicator.py`