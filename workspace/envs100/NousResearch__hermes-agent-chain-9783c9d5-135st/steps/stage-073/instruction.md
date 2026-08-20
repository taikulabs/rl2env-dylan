**fix: sanitize surrogate characters from clipboard paste to prevent UnicodeEncodeError**

## Summary

Pasting text from rich-text editors (Google Docs, Word, etc.) into the CLI can inject lone surrogate characters (U+D800..U+DFFF) that are invalid in UTF-8. The OpenAI SDK serializes messages with `ensure_ascii=False`, then encodes to UTF-8 for the HTTP body — surrogates crash this with:

```
UnicodeEncodeError: 'utf-8' codec can't encode character '\udce2' in position 394333: surrogates not allowed
```

The error was classified as a non-retryable `ValueError` (since `UnicodeEncodeError` inherits from `ValueError`), so the user saw:
```
Non-retryable client error (HTTP None). Aborting.
```

## Fix

Three-layer approach:

1. **Primary (run_agent.py):** Sanitize `user_message` at the top of `run_conversation()` — replaces surrogates with U+FFFD (Unicode replacement character) before they enter the message pipeline.

2. **CLI (cli.py):** Sanitize in `chat()` before appending to `conversation_history` — prevents surrogates from persisting in the CLI's session history across turns.

3. **Safety net (run_agent.py error handler):** If a `UnicodeEncodeError` still occurs (surrogates in conversation history or tool results), sanitize the entire messages list in-place and retry once. Also excludes `UnicodeEncodeError` from `is_local_validation_error` so it's no longer classified as non-retryable.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_surrogate_sanitization.py`