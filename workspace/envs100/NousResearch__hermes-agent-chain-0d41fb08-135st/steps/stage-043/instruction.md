**fix(error_classifier): disambiguate usage-limit patterns in _classify_by_message**

## What does this PR do?

Fixes a bug in `_classify_by_message` where messages containing usage-limit patterns (e.g. `"usage limit exceeded, try again in 5 minutes"`) arriving **without an HTTP status code** fell through to `FailoverReason.unknown` instead of being correctly classified as `rate_limit` or `billing`.