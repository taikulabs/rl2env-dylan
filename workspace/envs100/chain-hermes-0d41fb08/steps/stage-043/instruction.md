**fix(error_classifier): disambiguate usage-limit patterns in _classify_by_message**

## What does this PR do?

Fixes a bug in `_classify_by_message` where messages containing usage-limit patterns (e.g. `"usage limit exceeded, try again in 5 minutes"`) arriving **without an HTTP status code** fell through to `FailoverReason.unknown` instead of being correctly classified as `rate_limit` or `billing`.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_error_classifier.py`