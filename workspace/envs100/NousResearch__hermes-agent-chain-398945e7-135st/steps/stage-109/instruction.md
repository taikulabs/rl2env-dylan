**fix(codex-transport): preserve extra_headers for xAI Responses requests**

Salvage of #19229 by @Zyproth onto current main.

## Summary
When building xAI Responses API requests in `ResponsesApiTransport`, merge the `x-grok-conv-id` header into any existing `extra_headers` instead of overwriting them. Previously, caller-supplied headers via `request_overrides` were silently dropped.

## Changes
- agent/transports/codex.py: merge-instead-of-replace for xAI header path (+12/-1)
- tests: regression covering header preservation
- scripts/release.py: AUTHOR_MAP entry for @Zyproth

## Validation
scripts/run_tests.sh tests/agent/transports/test_codex_transport.py → 26 passed

Original PR: #19229