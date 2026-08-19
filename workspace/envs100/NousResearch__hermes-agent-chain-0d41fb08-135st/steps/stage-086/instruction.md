**fix: guard api_kwargs in except handler to prevent UnboundLocalError**

## Summary

Discord user gruman0 reported getting this error after updating:

```
Sorry, I encountered an error (UnboundLocalError).
cannot access local variable 'api_kwargs' where it is not associated with a value
```

**Root cause:** In the API retry loop in `run_conversation()`, `api_kwargs` is assigned inside the `try` block at line 7712 via `_build_api_kwargs()`. If that method throws an exception, the `except` handler tries to pass `api_kwargs` to `_dump_api_request_debug()` — but it was never assigned, causing `UnboundLocalError` that masks the real error.

Two unguarded references:
1. Line 8743: `_dump_api_request_debug(api_kwargs, reason="non_retryable_client_error")`
2. Line 8848: `_dump_api_request_debug(api_kwargs, reason="max_retries_exhausted")`

**Fix:**
- Initialize `api_kwargs = None` before the retry loop (same pattern as existing `response = None` guard)
- Guard both `_dump_api_request_debug` calls with `if api_kwargs is not None:`

**Note:** This fixes the masking bug so the *real* error surfaces. The user's underlying issue (whatever causes `_build_api_kwargs` to throw) will now show a descriptive error message instead of the opaque UnboundLocalError.