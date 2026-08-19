**fix(run-agent): rotate credential pool on billing-classified 400s**

## Summary

Salvage of #6940 by @helix4u — cherry-picked onto current main.

Bridges a gap where `classify_api_error()` correctly identifies billing-style HTTP 400 errors (e.g. Anthropic "out of extra usage") and sets `should_rotate_credential=True` with `reason=FailoverReason.billing`, but `_recover_with_credential_pool()` only checked raw status codes (401/402/429) and ignored the classified reason.

### Changes
- `_recover_with_credential_pool()` accepts optional `classified_reason` parameter
- Recovery behavior keyed off structured reason first, raw status code fallback
- Call site passes `classified.reason` from the error classifier
- New test: HTTP 400 with billing classification triggers immediate rotation

### Test results
- `recover_with_pool` tests: 7 passed
- `test_credential_pool_routing.py`: 14 passed