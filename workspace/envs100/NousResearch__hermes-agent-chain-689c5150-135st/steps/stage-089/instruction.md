**fix: warn on invalid context_length format in config.yaml**

## Summary

Non-integer `context_length` values (e.g. `256K`, `1M`) in config.yaml were silently ignored — the `int()` conversion threw ValueError, the except block set it to `None`, and the agent fell back to 128K auto-detection with zero user feedback.

This was reported by a community user (ChFarhan) who had a LiteLLM custom endpoint proxying GPT-5.4 (256K context) and Qwen 3.6 Plus (1M context). Both showed as 128K because their `context_length` config values couldn't be parsed.

## Changes

**`run_agent.py`** — Both silent-failure paths now:
- Log a WARNING with the invalid value and expected format
- Print a clear `⚠` message to stderr on CLI launch
- Still fall back gracefully to auto-detection

Two paths covered:
1. `model.context_length` in the model config section
2. `custom_providers[].models.<model>.context_length` per-model override

**`tests/run_agent/test_invalid_context_length_warning.py`** — 5 tests:
- Valid integer works silently
- String `'256K'` triggers warning + sets None
- Numeric string `'256000'` parses fine (no warning)
- Invalid value in custom_providers triggers warning
- Valid value in custom_providers works silently

## What it looks like

```
⚠ Invalid model.context_length in config.yaml: '256K'
  Must be a plain integer (e.g. 256000, not '256K').
  Falling back to auto-detected context window.
```