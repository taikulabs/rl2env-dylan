**fix(tools): write_file rejects missing 'content'/'path' instead of creating zero-byte files**

Salvage of #19119 by @Bartok9 onto current main.  — write_file silently creating zero-byte files when the model drops the `content` arg under context pressure, making downstream steps operate on empty data.

## Changes
- `tools/file_tools.py`: `_handle_write_file` validates `path` present+string, `content` key present (not just truthy so truncation still works), and `content` is string-typed. Returns actionable `tool_error` with remediation hint pointing at `execute_code` + `hermes_tools.write_file()` for large payloads (+24/-1)
- `tests/tools/test_file_tools.py`: 4 new regression tests covering missing content, missing path, explicit empty, non-string content (+38)

## Validation
- TestWriteFileHandler: 7/7 pass
- E2E: verified missing-content blocks without creating file; `content=""` still creates 0-byte file (truncation preserved); normal writes unchanged

. .

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_file_tools.py`