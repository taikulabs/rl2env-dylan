**fix(agent): salvage agent core PRs #6849 #6846**

## Summary

Salvage of 2 agent core PRs. Contributor authorship preserved.

**Cherry-picked:**

- **#6849** (MestreY0d4-Uninter) — Handle UnicodeEncodeError on ASCII-locale systems (`LANG=C`, common on Chromebooks/minimal containers). Adds `_strip_non_ascii()` fallback when the existing surrogate sanitizer doesn't help, plus fixes bare `.encode()` in cli.py suspend handler. 17 tests. +260/-19.

- **#6846** (WAXLYY) — Preserve quoted `@file` references with spaces. `@file:"C:\Users\My Project\main.py":7-9` was truncated at the first space because the regex used `\S+`. Adds quoted-path support with backreference matching. +78/-7.

**Closed (not merged):**
- **#6920** — Already fixed on main (retry counter reset at line 9199)
- **#6916** — Multimodal content doesn't reach the compressor in practice (vision tool returns text)
- **#6915** — Already fixed on main (fallback headers preserved from fb_client)

## Test results
31 tests pass (unicode_ascii_codec, context_references)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_context_references.py`