**fix(gateway): suppress duplicate voice transcripts**

Salvage of #19273 by @John-tip onto current main.

## Summary
Discord voice capture / STT occasionally emits the same utterance twice a few seconds apart, producing a second queued agent run and overlapping spoken replies. Dedup exact and near-exact repeats per `(guild, user)` over a 12-second window (SequenceMatcher ≥0.95 for near matches).

## Changes
- gateway/run.py: `_is_duplicate_voice_transcript()` + call site in `_handle_voice_channel_input`; `getattr(..., None)` fallback pattern for the new instance attribute (+54/-0)
- tests: exact and near-duplicate suppression regressions

## Validation
scripts/run_tests.sh tests/gateway/test_voice_command.py → 180 passed

Original PR: #19273

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_voice_command.py`