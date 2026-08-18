**fix(compression): replace dead summary_target_tokens with ratio-based scaling**

## Problem

The `summary_target_tokens` parameter in `ContextCompressor` was **dead code** — accepted in the constructor, stored on the instance, and never referenced anywhere in the compression logic. The actual summary budget was always computed from hardcoded module constants (`_SUMMARY_RATIO=0.20`, `_MAX_SUMMARY_TOKENS=8000`).

This caused two compounding problems:

1. **Config was silently ignored** — users had no real control over post-compression size
2. **Fixed budgets didn't scale with context window** — a fixed 20K tail budget and 8K summary cap meant switching from a 1M-context model (GPT-5.4) to a 200K model (MiniMax-2.7) would trigger compression that nuked 350K tokens of conversation history down to ~30K tokens (~91% information loss in one shot)

Additionally, `run_agent.py` hardcoded `summary_target_tokens=500` (even lower than the default 2500), and the threshold default of 0.50 (50%) was far too aggressive — compression fired at half the context window.

## Fix

### New: `summary_target_ratio` (replaces `summary_target_tokens`)
- Sets the post-compression target as a **fraction of context_length** (default: 0.40 = 40%)
- Tail token budget = `context_length × ratio` (scales with model)
- Summary cap = 5% of context, capped at 32K (was fixed 8K)
- Clamped to [0.10, 0.80] range

### Scaling examples:
| Model | Context | Threshold (80%) | Post-compression (~40%) |
|-------|---------|-----------------|------------------------|
| MiniMax-2.7 | 200K | 160K | ~80K |
| GPT-5.4 | 1M | 800K | ~400K |

### Other changes:
- `threshold_percent`: 0.50 → **0.80** (don't fire until 80% full)
- `protect_last_n`: 4 → **20** (~10 full turns survive)
- Both `target_ratio` and `protect_last_n` are now configurable via `config.yaml`
- Removed hardcoded `summary_target_tokens=500` from `run_agent.py`
- Updated `cli-config.yaml.example` with new options and docs

## Files changed
- `agent/context_compressor.py` — core fix
- `run_agent.py` — read new config params, remove dead hardcode
- `cli-config.yaml.example` — document new options
- `tests/agent/test_context_compressor.py` — 5 new tests + 1 fixture fix

## Tests
All 40 tests pass (34 compressor + 6 boundary).