**fix: pass resolved args to resolve_vision_provider_client()**

`resolve_vision_provider_client()` was receiving the raw `call_llm` parameters instead of the resolved provider/model/key/url from `_resolve_task_provider_model()`. This caused config overrides (`auxiliary.vision.provider`, etc.) to be silently discarded.

## Test Results

```
tests/agent/test_auxiliary_client.py:          98 passed
tests/agent/test_vision_resolved_args.py:       1 passed (new)
```

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_vision_resolved_args.py`