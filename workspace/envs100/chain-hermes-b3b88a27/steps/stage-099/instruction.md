**fix(compression): resolve missing config attribute in feasibility check**

## Problem

 ("fix(compression): pass configured context_length to feasibility check") introduced a reference to `self.config` in `_check_compression_model_feasibility()` to read the user's `auxiliary.compression.context_length` setting. However, `AIAgent` never stores the loaded config as an instance attribute — the config is loaded into a local variable `_agent_cfg` in `__init__()` (line 1271) and discarded after initialization.

This causes every session start with compression enabled to hit:

```
AttributeError: 'AIAgent' object has no attribute 'config'
```

The error is caught by the enclosing `try/except` and logged at DEBUG level as a non-fatal message, so it doesn't crash — but the configured `context_length` is silently ignored, defeating the purpose of the original fix.

## Why CI Didn't Catch It

The existing tests in `test_compression_feasibility.py` use `AIAgent.__new__(AIAgent)` to skip `__init__()` entirely, then manually wire up `agent.config = None` (or `agent.config = {...}`). This means the tests always had the attribute available and passed — but real `__init__()` never creates it.

## Root Cause

`_check_compression_model_feasibility()` references `self.config` (line 2028), but the config dict is only stored in a local variable `_agent_cfg` inside `__init__()` and never assigned to `self`.

## Fix

1. Store the loaded config as `self._config` in `__init__()` (private attribute, right after the existing `_agent_cfg` assignment)
2. Update the reference in `_check_compression_model_feasibility()` from `self.config` → `self._config`
3. Update the test fixture and test cases to use `_config` instead of `config`

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/run_agent/test_compression_feasibility.py`