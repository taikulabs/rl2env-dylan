**fix: log prompt builder skill parsing fallbacks**

## Summary
- add debug logging for the remaining silent prompt_builder skill parsing fallbacks
- preserve the existing permissive return behavior when skill metadata cannot be read
- add regression tests covering both fallback paths and emitted debug logs

## Context
This supersedes closed PR #1270 after its branch was deleted during merge cleanup. It still replaces the still-relevant prompt_builder portion of #914, whose other logging changes were already superseded on main.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_prompt_builder.py`