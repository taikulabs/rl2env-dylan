**fix: DeepSeek V3 parser drops multi-tool calls**

## Summary
- 
- switch the DeepSeek V3 parser regex captures from greedy to non-greedy so multiple tool calls parse correctly
- add dedicated DeepSeek V3 parser coverage for no-call, single-call, multi-call, and preceding-text cases

## Why
DeepSeek V3 responses with 2+ tool calls could collapse into one parsed call because the parser used greedy `.*` with `re.DOTALL`.

Salvages #992 with contributor credit preserved.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_tool_call_parsers.py`