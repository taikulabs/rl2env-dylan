**feat: add direct endpoint overrides for auxiliary and delegation**

## Summary
- salvage PR #1370 onto current main and keep direct endpoint overrides for auxiliary tasks and delegation
- wire the current vision routing path through task-level base_url/api_key overrides instead of regressing to the pre-refactor helper flow
- keep direct endpoint key fallback scoped to explicit task/delegation keys or OPENAI_API_KEY, add regression coverage, and tighten messaging env isolation in tests