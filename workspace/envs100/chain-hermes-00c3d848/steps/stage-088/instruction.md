**fix(compression): notify users when configured aux model fails even if main-model fallback recovers**

## Summary

When a user's configured `auxiliary.compression.model` errors out but compression recovers by retrying on the main model, we now still tell the user their aux model is broken. Before: silent recovery hid a misconfig only they could fix.

Distinct from the existing ⚠️ dropped-turns warning — this is an ℹ note confirming context is intact while flagging the config problem.

## Changes

`agent/context_compressor.py`
- Track `_last_aux_model_failure_model` + `_last_aux_model_failure_error` on the compressor. Set in both retry-on-main branches (the 404/503 fast-path and the unknown-error best-effort path from #16774), before `summary_model` is cleared. Cleared at `compress()` start + `on_session_reset()` so warnings don't leak across runs.

`gateway/run.py`
- Hygiene auto-compress: after the existing fallback-used check, elif on aux-failure → send `ℹ️ Configured compression model '<model>' failed (<err>). Recovered using your main model — context is intact — but you may want to check auxiliary.compression.model in config.yaml.` via the platform adapter with `thread_id` metadata preserved.
- `/compress` command: same elif pattern, ℹ line appended to the reply.

`run_agent.py`
- `_compress_context`: after the existing `_last_summary_error` warning emit, an `else` branch emits the aux-failure notice via `_emit_warning` for CLI users. Deduped on `(model, error)` via `_last_aux_fallback_warning_key` so repeat compactions don't spam.

## Validation

| Scenario | Before | After |
|---|---|---|
| Aux model 404, retry-on-main succeeds | silent | ℹ note with model name + error + config pointer |
| Aux model 400, retry-on-main succeeds | silent | ℹ note |
| Summary fully fails → placeholder inserted | ⚠️ warning (existing) | ⚠️ warning (unchanged) |
| Default config (empty aux model), main-only path | silent | silent (no false positive) |

```
scripts/run_tests.sh tests/agent/test_context_compressor.py tests/gateway/test_session_hygiene.py tests/gateway/test_compress_command.py tests/run_agent/test_compression_feasibility.py
105 passed in 4.12s
```

4 new tests:
- compressor: 404 / 400 retry paths now assert `_last_aux_model_failure_*` is populated.
- `TestAuxModelFallbackSurfacedToCallers`: compress()-level exposure + clear-on-next-call.
- `test_compress_command_surfaces_aux_model_failure_even_when_recovered`: /compress ℹ line + "context is intact".
- `test_session_hygiene_informs_user_when_aux_model_fails_but_recovers`: hygiene-path ℹ note lands in the right thread.

 (retry-on-main) and #16771 (original gateway warning plumbing).

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_context_compressor.py`
- `tests/gateway/test_compress_command.py`
- `tests/gateway/test_session_hygiene.py`