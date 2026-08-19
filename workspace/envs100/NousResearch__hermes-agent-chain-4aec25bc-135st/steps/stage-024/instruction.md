**feat(cli): show ▶ N indicator in status bar for running /background tasks**

## Summary
Surfaces live /background task count as `▶ N` in the prompt_toolkit status bar so users can see at a glance that bg tasks exist and are running — no need to ask the agent (which has no visibility into bg sessions by design).

. Closes the UX gap that motivated #8592 with ~25 LOC instead of ~840.

## What it looks like

```
Idle:     ⚕ claude-opus-4.6 │ ctx -- │ -- │ 0s
1 task:   ⚕ claude-opus-4.6 │ ctx -- │ -- │ ▶ 1 │ 0s
3 tasks:  ⚕ claude-opus-4.6 │ ctx -- │ -- │ ▶ 3 │ 0s
```

## Changes
- `cli.py` (+25): `_get_status_bar_snapshot` reports `active_background_tasks` from `len(self._background_tasks)`. `▶ N` fragment added to medium (<76) and wide (>=76) status-bar tiers. Narrow (<52) stays minimal — it's already cramped.

## Why this works automatically
- `_get_status_bar_fragments` is called via lambda on every redraw, so the count refreshes naturally as the user types / spinner ticks.
- The bg thread already calls `self._app.invalidate()` in its `finally` block, so the indicator disappears immediately when the last task completes.
- `_background_tasks` is the existing source of truth; entries are removed in the task thread's finally block, so `len()` reflects truly-running tasks. `len()` on a CPython dict is atomic.

## Why not the bigger feature
PR #8592 proposed artifacts + `/bg status|log|files|kill` + foreground context injection (~840 LOC). The actual user complaint was a UX gap: there's no visible signal that a bg task exists, so users invent the workaround of asking the agent about it. A persistent status-bar indicator removes the need to ever ask, which removes the bug class. Slash-command inspection and artifact persistence can be added later if there's demand.

## Validation
| | Before | After |
|---|---|---|
| tests/cli/ | 706 pass | 715 pass (+9 new) |
| Existing bg/status tests | pass | pass |
| Visual smoke at widths 40/70/120 | n/a | renders cleanly, no overflow |