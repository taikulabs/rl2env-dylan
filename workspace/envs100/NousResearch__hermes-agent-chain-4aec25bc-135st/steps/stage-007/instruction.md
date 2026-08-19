**security: sanitize tool error strings before injecting into model context (salvage of #3838 piece 3/3)**

## Summary
Sanitize tool error strings before they enter the model's `tool` message content. Strips XML role tags (`tool_call`, `function_call`, `result`, `response`, `output`, `input`, `system`, `assistant`, `user`), CDATA sections, and markdown code fences; caps at 2000 chars; wraps with `[TOOL_ERROR]` prefix.

Defense-in-depth — `json.dumps` already handles wire-layer escaping so framing tokens in exceptions can't break message structure, but the model still *reads* those tokens and they nudge it toward role-confusion framing.

## Why this is a salvage of #3838, not the whole PR
Original scout PR ported three ironclaw resilience features. Two are already implemented far more thoroughly on current main:
- **#1632 truncated tool calls** → `run_agent.py` L8147 / L12209 / L13012 (retry counter, length rewrite, refusal after 2nd consecutive truncation)
- **#1677 / #1720 empty-response recovery** → `run_agent.py` L4500 / L15090+ (scaffolding stripper, multi-stage nudge, fallback model activation, dedicated `empty-response-recovery.md` skill ref)

Only **#1639 (error sanitization)** wasn't on main — that's what this PR salvages.

## Adjustment vs original
The original PR only patched `handle_function_call`'s outer `except`, but that's a *secondary* guard. `tools/registry.py::dispatch` has its own try/except that catches most tool exceptions first and returns them raw — so the original sanitization would have been bypassed in the primary error path. This PR patches both, with `registry.py` doing a defensive try/except around the sanitizer import so the error path can never block on sanitization itself.

## Changes
- `model_tools.py` (+45): `_sanitize_tool_error()` + compiled regexes for role tags / fences / CDATA; wired into existing outer `except`
- `tools/registry.py` (+11): dispatch error path routes through `_sanitize_tool_error`, with safe fallback if import fails
- `tests/test_sanitize_tool_error.py` (+135): 16 tests covering role tags (case-insensitive), CDATA, code fences, truncation, envelope, real exception-path integration

## Validation
| | Result |
|---|---|
| New tests | 16/16 |
| `tests/tools/` | 5073/5075 (2 pre-existing parallel-isolation failures, unrelated) |
| `tests/agent/` | 2984/2985 (1 pre-existing aux client failure, unrelated) |
| `tests/tools/test_delegate.py` in isolation | 127/127 |

## Source
, originally scouted in #3838.