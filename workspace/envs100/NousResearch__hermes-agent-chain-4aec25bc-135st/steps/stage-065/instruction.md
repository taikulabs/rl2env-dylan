**fix(compress): make abort-on-summary-failure opt-in via config flag**

## Summary
PR #28102 changed the default — summary-failure now aborts compression instead of dropping the middle window with a placeholder. That was wrong; gate the new behavior behind a config flag and restore the original default.

## Default behavior (unchanged from before #28102)
`compression.abort_on_summary_failure: false` → on aux LLM failure, insert a static "summary unavailable" placeholder and drop the middle window (legacy fallback).

## Opt-in behavior
`compression.abort_on_summary_failure: true` → on aux LLM failure, abort compression entirely. Messages preserved unchanged, `_last_compress_aborted=True`, gateway/CLI surface the "compression aborted, run /compress to retry" warning.

## Changes
- `hermes_cli/config.py`: new `compression.abort_on_summary_failure` key (default False) with inline docs
- `agent/agent_init.py`: read flag, pass to ContextCompressor
- `agent/context_compressor.py`: `__init__` takes `abort_on_summary_failure` kwarg; `compress()` failure branch gates the abort behind the flag; restored legacy fallback path for default mode
- `tests/agent/test_context_compressor.py`: original tests restored (fallback as default); new `TestAbortOnSummaryFailure` class covers opt-in mode

Gateway/CLI plumbing from #28102 (force=True on /compress, abort-detection warnings, `gateway.compress.aborted` locale key) stays — those paths only fire when `_last_compress_aborted` is True, which only happens when the flag is on.

## Validation
| | Result |
|---|---|
| tests/agent/test_context_compressor.py | 83/83 |
| tests/gateway/test_session_hygiene.py | 23/23 |
| tests/gateway/test_compress_command.py | 4/4 |
| tests/agent/test_i18n.py | 43/43 |