**fix(kimi): force 0.6 on main chat path**

Salvage of #11883 onto current main, preserving @helix4u authorship.

## Summary
kimi-for-coding now sends `temperature=0.6` on the main chat-completions path. Previously only the auxiliary client and `flush_memories` forced 0.6, so a normal user turn still returned `HTTP 400: invalid temperature: only 0.6 is allowed for this model`.

## Changes
- `run_agent.py`: apply `_fixed_temperature_for_model()` in `_build_api_kwargs` (covers non-streaming + streaming main paths via `stream_kwargs = {**api_kwargs}`)
- `run_agent.py`: same override applied to the iteration-limit summary and retry-summary paths
- `tests/run_agent/test_provider_parity.py`: regression test asserting `kimi-for-coding` forces `temperature == 0.6`

## Validation
| | Before | After |
|---|---|---|
| `kimi-for-coding` main turn | 400 invalid temperature | temperature=0.6 sent |
| `tests/run_agent/test_provider_parity.py tests/agent/test_auxiliary_client.py` | 133 passed | 134 passed |

Credit: @helix4u.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/run_agent/test_provider_parity.py`