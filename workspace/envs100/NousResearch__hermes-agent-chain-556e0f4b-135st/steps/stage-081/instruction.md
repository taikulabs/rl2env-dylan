**fix: respect DashScope v1 runtime mode for alibaba (salvage #2024)**

## Summary
Based on PR #2024 by @kshitijk4poor, applied manually onto current main.

The Alibaba provider had a hardcoded branch in `resolve_runtime_provider()` that always forced `api_mode='anthropic_messages'`, regardless of the configured base URL. This broke the OpenAI-compatible DashScope coding endpoint (`/v1`) because setup saved the URL correctly but runtime forced Anthropic mode.

### Fix
Removes the Alibaba-specific branch and lets it go through the generic API-key provider path, which already handles mode detection correctly:
- Default URL `/apps/anthropic` → detected by `endswith('/anthropic')` → `anthropic_messages`
- Coding URL `/v1` → no match → `chat_completions` (correct)

### Tests
2 new tests verifying both Alibaba endpoint modes.

## Verification
- Runtime provider tests: 31/31 passed

## Credit
Original work by @kshitijk4poor in #2024. Contributor authorship preserved.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_runtime_provider_resolution.py`