**fix: escape parens and braces in fork bomb regex pattern**

## Summary
- 
- add the contributor's targeted regression tests for the classic `:(){ :|:& };:` form, a whitespace variant, and a safe colon-containing command

## Contributor credit
Salvages PR #1078 by cherry-picking the contributor commit onto current main with authorship preserved.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_approval.py`