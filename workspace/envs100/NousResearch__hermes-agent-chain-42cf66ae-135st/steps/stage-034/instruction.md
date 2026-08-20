**refactor: salvage adapter and CLI cleanup from PR #939**

## Summary
- salvage the current-main-safe cleanup work from PR #939 by @kshitijk4poor
- deduplicate Discord slash command dispatch and local file attachment helpers
- deduplicate Slack file uploads while preserving thread metadata behavior on current main
- extract shared CLI session relative-time formatting and hoist browser cleanup constants
- add screenshot cleanup throttling coverage

## Contributor credit
This PR salvages the substantive cleanup work from #939 onto current main with adaptation for newer gateway behavior.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_send_image_file.py`