**fix+feat: agent core fixes (Bucket P — 4 PRs)**

## Summary
Four agent core fixes salvaged from #6951, #6953, #6950, #6944. All contributor authorship preserved.

### 1. feat(delegation): configurable reasoning_effort for subagents (#6951, @hermes-agent-dhabibi)
New `delegation.reasoning_effort` config key. Subagents can run at different thinking levels. 4 tests.

### 2. fix: copilot Responses-API wrapping for auxiliary tasks (#6953, @hermes-agent-dhabibi)
GPT-5+ on Copilot needs Responses API but aux client created plain OpenAI client. Now wraps in CodexAuxiliaryClient when needed. 3 tests.

### 3. fix(tools): dead code removal + brace path hardening (#6950, @luyao618)
Unreachable code in `_is_likely_binary()`, `.format()` → `.replace()` in `_check_lint()` to handle `{curly brace}` file paths. 16 tests.

### 4. fix(compression): truthful manual compression feedback (#6944, @aquaright1)
`/compress` no longer shows "✅ Compressed" when nothing changed. Shared `summarize_manual_compression()` helper detects no-ops and explains token estimate increases. Both CLI and gateway updated. 2 test files.

## Test results
26 targeted tests passing. All 6 modified files compile clean.