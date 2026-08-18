**fix(skills): block category path traversal in skill manager**

## Summary

Validates category names in `_create_skill()` before using them as filesystem path segments. Previously, values like `../escape` or `/tmp/pwned` could write skill files outside `~/.hermes/skills/`.

Salvaged from PR #1939 by Gutslabs.

## Changes

- Added `_validate_category()` that rejects slashes, backslashes, absolute paths, and characters outside `VALID_NAME_RE`
- Called before `_resolve_skill_dir()` in `_create_skill()`
- 5 new tests: traversal, absolute paths, valid categories, integration with `_create_skill`

## E2E verified

- `../escape` → blocked, nothing written outside skills/
- `/tmp/pwned` → blocked
- `..\escape` → blocked
- Valid categories (`devops`, `ml-ops_v2`, etc.) → work correctly
- 51/51 skill manager tests passing