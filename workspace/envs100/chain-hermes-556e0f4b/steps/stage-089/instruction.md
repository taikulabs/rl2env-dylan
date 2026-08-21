**fix(context): block @ references from reading secrets outside the workspace**

## What does this PR do?
Fixes a safety bug in `@` context reference expansion.

Previously, CLI `@file:` / `@folder:` expansion defaulted to an unrestricted root, so absolute paths outside the current workspace could be attached directly into the prompt. Gateway expansion also allowed references to sensitive paths under the messaging working directory, including files like `.hermes/.env` and `.ssh/id_rsa`.

This change makes `@` references default to the current working directory boundary and blocks known sensitive credential / internal Hermes paths even when they are technically inside the allowed root.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_context_references.py`