**fix(agent): retry malformed anthropic stream parser errors (salvage #26751)**

Salvage of #26751 by @helix4u onto current `main` — original branch was 13 commits behind. Cherry-picked unchanged; helix4u's authorship preserved.

## Summary

Treats Anthropic-stream parser `ValueError`s like `"expected ident at line 1 column 149"` as transient malformed-stream errors and routes them through the existing stream-retry loop instead of aborting as `Non-retryable error (HTTP None)`.

Reported on Discord by Stefan — MiniMax via the Anthropic-compatible endpoint emits a malformed event-stream frame; the Anthropic SDK raises a plain `ValueError`; the local-validation guard catches it and the whole turn dies. Same shape as the merged `JSONDecodeError` retry fix — malformed provider wire data is provider trouble, not local validation.

## Changes

- `run_agent.py` — new `_is_provider_stream_parse_error()` (api_mode=anthropic_messages + literal substring `"expected ident at line"`, excludes UnicodeEncodeError/JSONDecodeError), wired into the in-stream retry classifier, the post-stream retry classifier, and the outer `is_local_validation_error` exclusion list. New status string when retries exhaust.
- `tests/run_agent/test_streaming.py` — two regression tests: malformed parser ValueError retries; generic ValueError still doesn't.

## Validation

`scripts/run_tests.sh tests/run_agent/test_streaming.py` → **36 passed**.

.