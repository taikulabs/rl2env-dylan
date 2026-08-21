**fix(agent): downgrade xhigh→max on Anthropic pre-4.7 adaptive models**

## What does this PR do?

Fixes a regression from #11161 (Claude Opus 4.7 migration, merged as
[0517ac3e](https://github.com/NousResearch/hermes-agent/)
earlier today): Hermes now 400s on every request when the user has
`reasoning_effort=xhigh` set and switches to a pre-4.7 Anthropic adaptive model
(Opus/Sonnet 4.6).

### Repro (before this fix)

```
hermes config set model anthropic/claude-opus-4-6
hermes config set agent.reasoning_effort xhigh
hermes chat -q "hi"
```

```
API call failed: BadRequestError [HTTP 400]
Provider: anthropic  Model: claude-opus-4-6
Error: HTTP 400: This model does not support effort level 'xhigh'.
       Supported levels: high, low, max, medium.
```

### Root cause

PR #11161 changed `ADAPTIVE_EFFORT_MAP["xhigh"]` from `"max"` (the pre-migration
alias) to `"xhigh"` to preserve the new 4.7 level as distinct from `max`. That
was correct for Opus 4.7. But per Anthropic's
[migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide),
Opus/Sonnet **4.6** only expose 4 effort levels (low/medium/high/max) — `xhigh`
was added on 4.7 as the recommended default for coding/agentic use:

| Level | 4.6 | 4.7 |
|-------|:---:|:---:|
| max   | ✅  | ✅  |
| xhigh | ❌  | ✅ (new) |
| high  | ✅  | ✅  |
| medium| ✅  | ✅  |
| low   | ✅  | ✅  |

The SDK typing agrees — `anthropic.types.OutputConfigParam.effort:
Literal["low","medium","high","max"]` in `anthropic==0.94.0`. TypedDict isn't
runtime-validated, so the API rejects `xhigh` on 4.6 directly with a 400.

Users who prefer `xhigh` as their default (per the migration guide
recommendation) get a hard 400 the moment they switch back to a 4.6 model —
common during A/B, cost comparison, or when 4.7 hits capacity.

### Fix

Make the adaptive-effort mapping model-aware. Add `_supports_xhigh_effort()`
predicate alongside the existing `_supports_adaptive_thinking()` and
`_forbids_sampling_params()` predicates — same substring-match pattern, matches
`4-7` / `4.7`. On pre-4.7 adaptive models, downgrade `xhigh → max` (the
strongest effort those models accept — restores pre-migration behavior). On
4.7+, keep `xhigh` as a distinct level.

## Related Issue

No open issue — self-reported during a live session right after #11161 shipped.
Regression source: [0517ac3e](https://github.com/NousResearch/hermes-agent/).

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_anthropic_adapter.py`