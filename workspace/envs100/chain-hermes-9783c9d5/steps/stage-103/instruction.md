**fix(skills): validate hub bundle paths before install**

Salvage of PR #3942. Fixes path traversal vulnerabilities in the Skills Hub quarantine/install flow.

**Problem:** `quarantine_bundle()` trusted bundle-controlled file paths and wrote them to disk before scanning. A malicious bundle with `../../../escape.txt` could write files outside the quarantine directory before the security scan ran.

**Fix:** Central `_normalize_bundle_path()` validates all bundle-controlled paths before any disk write:
- Rejects absolute paths, `..` traversal, Windows drive letters, backslash normalization
- `quarantine_bundle()` validates ALL file paths before writing anything
- `install_from_quarantine()` validates skill name/category + checks quarantine path is under quarantine root
- Well-known source validates index file paths before fetching
- ZIP handling: replaces weak `".." in name` substring check with normalized path validation
- CLI surfaces blocked installs cleanly with audit logging

**Tests:** 80 passed (3 new regression tests for traversal, absolute paths, unsafe well-known index)

Co-authored-by: Gutslabs <gutslabsxyz@gmail.com>

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_skills_hub.py`