**fix: refresh Anthropic OAuth before stale env tokens**

## Summary
- prefer refreshable Claude Code credentials over static persisted Anthropic OAuth env tokens
- preflight Anthropic credential refresh before native Messages API calls and keep 401 retry as a fallback
- stop copying Claude Code credential-file auth into ANTHROPIC_TOKEN during setup; rely on Claude's credential store directly when available
- clarify Anthropic setup docs, env var semantics, and provider runtime behavior
- add regression coverage for env-token shadowing, setup flow persistence, and Anthropic client rebuild behavior

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_anthropic_adapter.py`
- `tests/test_anthropic_oauth_flow.py`
- `tests/test_anthropic_provider_persistence.py`
- `tests/test_run_agent.py`