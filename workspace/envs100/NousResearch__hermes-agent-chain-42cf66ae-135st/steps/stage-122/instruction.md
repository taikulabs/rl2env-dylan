**feat: add persistent CLI status bar and usage details**

## Summary

Salvage of PR #1104 by @kshitijk4poor. .

Adds a persistent status bar to the CLI that shows model name, context window usage (with visual bar), estimated cost, and session duration.

### Status Bar

```
 ⚕ claude-sonnet-4-20250514 │ 12.4K/200K │ [██████░░░░] 6% │ $0.06 │ 15m
```

Responsive — degrades for narrow terminals:
- **≥ 76 cols**: full layout with context bar
- **52–75 cols**: compact (percent, cost, duration)
- **< 52 cols**: minimal (model + duration only)

Color-coded context thresholds: green (< 50%), yellow (50–80%), orange (80–95%), red (≥ 95%).

### Enhanced `/usage` Command

Now shows model name, per-category cost breakdown (input/output), session duration. Zero-priced provider models (GLM, Kimi, MiniMax) correctly show "n/a" instead of "$0.00".

### Shared Pricing Module

Extracts pricing table + cost estimation + duration formatting from `agent/insights.py` into `agent/usage_pricing.py`. Eliminates duplicate code between `/insights` and `/usage`. Uses `Decimal` arithmetic to avoid floating-point rounding.

### Files Changed

| File | Change |
|------|--------|
| `agent/usage_pricing.py` | **NEW** — shared pricing table, cost estimation, formatting helpers |
| `agent/insights.py` | Refactored to import from `usage_pricing` |
| `cli.py` | Status bar widget, enhanced `/usage`, 1Hz idle refresh |
| `tests/test_cli_status_bar.py` | **NEW** — status bar + usage report tests |
| `tests/test_insights.py` | Zero-priced model assertion |

### Salvage Fixes

- Resolved merge conflict with voice status bar (both coexist in layout)
- Fixed `_format_context_length` import (moved to `hermes_cli/banner.py` since PR was written)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_cli_status_bar.py`
- `tests/test_insights.py`