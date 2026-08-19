**fix(curator): preserve last_report_path in state**

Salvages #18058 by @Yukipukii1 onto current main.

## Summary
`hermes curator status` now shows the last report path instead of always showing none. Root cause: curator wrote `last_report_path` into state but `load_state()` only preserved keys present in `_default_state()`, silently dropping it on the next read.

## Changes
- `agent/curator.py`: add `last_report_path` to `_default_state()`
- `tests/agent/test_curator.py`: regression test for save → load round-trip

## Validation
- `scripts/run_tests.sh tests/agent/test_curator.py` → 39 passed
- E2E: save with `last_report_path` set → load → field preserved (previously dropped)

Authored by @Yukipukii1 (commit authorship preserved). .