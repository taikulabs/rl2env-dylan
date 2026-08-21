**fix(kimi): cover remaining fixed-temperature bypasses**

Salvage of #11921 by @helix4u onto current main.

Closes the last three direct `chat.completions.create()` call sites that bypassed the kimi-for-coding temperature=0.6 contract.

## Changes
- `tools/approval.py`: route `_smart_approve` through `call_llm(task="approval")` — picks up `_fixed_temperature_for_model()` from `_build_call_kwargs()` automatically
- `trajectory_compressor.py`: apply fixed-temperature helper before sync/async raw-client fallback
- `mini_swe_runner.py`: inject fixed temperature into kwargs when the model has a fixed contract
- Regression tests for all four call paths

## Validation
| | Result |
|---|---|
| Targeted suite (approval + compressor + mini_swe + aux) | 214 passed |

Authored-by: @helix4u. .

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_mini_swe_runner.py`
- `tests/test_trajectory_compressor.py`
- `tests/test_trajectory_compressor_async.py`
- `tests/tools/test_approval.py`