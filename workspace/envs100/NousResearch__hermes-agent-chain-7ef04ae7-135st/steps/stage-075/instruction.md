**fix(agent): stop over-cap max_tokens 400s from death-looping into compression**

## Summary
An over-cap `model.max_tokens` no longer death-loops into context compression — the over-cap 400 is either retried with a safe output cap (DashScope/Qwen) or fails fast with an actionable message, instead of compressing a tiny conversation until "cannot compress further".

Root cause: a provider 400 about the output cap (e.g. DashScope `Range of max_tokens should be [1, 65536]`) contains the substring `max_tokens`, which trips `_CONTEXT_OVERFLOW_PATTERNS` and is classified as `context_overflow`. On providers whose wording `parse_available_output_tokens_from_error()` didn't recognize, the smart-retry was skipped and control fell into the compression fallback — which re-sends the same oversized `max_tokens`, gets the identical 400, and loops.

This is the same failure class the existing GPT-5 `max_tokens` guard already protects against; the fix mirrors it rather than teaching the parser one more phrasing.

## Changes
- `agent/model_metadata.py`:
  - `parse_available_output_tokens_from_error()` now recognizes the DashScope/Alibaba `Range of max_tokens should be [1, N]` form and returns `N`, so the smart-retry caps output and retries **without** compressing.
  - new `is_output_cap_error()` — a broader yes/no gate that identifies output-cap 400s even when no number is parseable, while excluding genuine input overflows.
- `agent/conversation_loop.py`: when the error is output-cap-shaped but unparseable, fail fast (`Lower model.max_tokens in config.yaml`) instead of routing into compression — kills the whole death-loop class for any provider.
- `tests/test_output_cap_parsing.py`: DashScope range parsing + `is_output_cap_error` coverage (input-overflow and GPT-5-param negatives included).

## Validation
| scenario | before | after |
|---|---|---|
| DashScope `Range of max_tokens should be [1, 65536]` | compress → same 400 → death-loop | parse 65536 → retry safe cap, no compression |
| Unknown output-cap wording (unparseable) | death-loop | fail fast, name `model.max_tokens` |
| Real input overflow mentioning max_tokens | compress (correct) | compress (unchanged) |
| GPT-5 unsupported-param 400 | format_error fallback | format_error fallback (unchanged) |

Targeted suites green: `test_output_cap_parsing.py`, `test_ctx_halving_fix.py`, `test_error_classifier.py`, `test_model_metadata.py`, `test_413_compression.py` (341 tests). E2E confirmed the full classify→loop chain for both the DashScope and unknown-wording paths.

## Infographic
![max_tokens death-loop fix](https://v3b.fal.media/files/b/0aa05be2/BV7Xu_3Uha1EVIh9skbS5_acuEhePA.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_output_cap_parsing.py`