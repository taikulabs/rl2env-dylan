**fix: restore Codex fallback auth-store lookup**

## Summary
- fall back to the profile auth store when the openai-codex credential pool exists but has no selectable runtime entry
- keep `_try_codex()` on the same path so fallback-to-Codex does not abort early as 'provider not configured'
- add regression coverage for both code paths

## Why
Anthropic 'out of extra usage' errors were reaching Hermes fallback logic, but fallback to `openai-codex/gpt-5.4` failed even though a valid Codex OAuth token existed in `auth.json`. The pool layer could report 'present' while returning no selected entry, which caused the resolver to return `None` instead of checking the stored OAuth token.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_auxiliary_client.py`