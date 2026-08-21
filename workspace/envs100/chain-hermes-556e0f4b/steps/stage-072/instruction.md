**fix(redact): safely handle non-string inputs (salvage #2369)**

## Summary

Salvage of PR #2369 by @aydnOktay. Cherry-picked cleanly onto current main.

`redact_sensitive_text()` now handles non-string inputs defensively:
- Returns `None` early for `None` input (explicit check instead of relying on truthiness)
- Coerces other non-string values (int, dict, etc.) to `str` before applying regex patterns
- Prevents `TypeError` crashes when non-string values flow through logging/tool-output paths

Two new tests: int coercion and dict coercion with redaction.

**Tests:** 31/31 redact tests passing.

Credit: @aydnOktay (original author, commit authorship preserved).

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_redact.py`