**fix(cli): silence tirith prefetch install warnings at startup**

## Summary
- stop Hermes CLI and gateway startup prefetch from surfacing tirith auto-install warnings to end users
- keep tirith prefetch behavior, but run it in a quiet mode so expected install misses like missing `cosign` only log at debug level during startup
- preserve existing behavior for real on-demand scans and add regression coverage for the quiet prefetch path

## Root cause
Hermes calls `ensure_installed()` during CLI and gateway startup to prefetch the tirith scanner. When tirith is not already installed and `cosign` is missing, the background install path logs warnings like:

`tirith install skipped: cosign not found on PATH...`

That warning is expected for startup prefetch, but it leaks into the user-facing startup experience.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_tirith_security.py`