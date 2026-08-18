**fix(approval): honor bare YAML approvals.mode: off**

Salvaged from PR #2563 by @tumf.

## Problem
YAML 1.1 parses unquoted `off` as boolean `False`. A config like:
```yaml
approvals:
  mode: off
```
results in `_get_approval_mode()` returning `False` instead of `"off"`, so the approval system keeps prompting despite the user's intent.

## Fix
Added `_normalize_approval_mode()` that maps `False` → `"off"`, `True` → `"manual"`, and normalizes string values.

## Tests
76 approval tests pass, including 2 new regression tests for the YAML boolean edge case.