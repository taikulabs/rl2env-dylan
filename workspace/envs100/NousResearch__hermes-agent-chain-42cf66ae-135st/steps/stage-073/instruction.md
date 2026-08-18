**fix: refresh Anthropic OAuth before stale env tokens**

## Summary
- prefer refreshable Claude Code credentials over static persisted Anthropic OAuth env tokens
- preflight Anthropic credential refresh before native Messages API calls and keep 401 retry as a fallback
- stop copying Claude Code credential-file auth into ANTHROPIC_TOKEN during setup; rely on Claude's credential store directly when available
- clarify Anthropic setup docs, env var semantics, and provider runtime behavior
- add regression coverage for env-token shadowing, setup flow persistence, and Anthropic client rebuild behavior