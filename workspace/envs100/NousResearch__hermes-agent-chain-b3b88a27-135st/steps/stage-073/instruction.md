**feat(steer): /steer <prompt> injects a mid-run note after the next tool call**

## Summary

Adds `/steer <prompt>` — a mid-run user-message injection that lands between tool-call iterations without interrupting the agent or creating a new user turn. The text is appended to the last tool result's content once the current tool batch finishes, so the model sees it inline with tool output on its next iteration.

Sits between the existing `/queue` (turn boundary) and interrupt. Wired into CLI, gateway (Telegram/Discord/Slack/etc.), and the new Ink TUI.

`@OutThisLife` — please review the TUI surface (see `ui-tui/` changes below); that's a ~35-line slash command plus a response type.

## Why this shape

- **Role alternation preserved.** The steer text is appended to an existing `role:"tool"` message's `content`. No synthetic user turn is inserted mid-loop — matches the invariant in `AGENTS.md`.
- **Cache-safe.** Tool-result messages are tail-of-prefix; they already invalidate per turn. No additional cache break.
- **Clear provenance marker.** Injected as `[USER STEER (injected mid-run, not tool output): …]` so the model doesn't mistake it for tool output.

## Changes

| File | What |
|---|---|
| `hermes_cli/commands.py` | Register `/steer` + add to `ACTIVE_SESSION_BYPASS_COMMANDS` so Level‑1 base-adapter guard dispatches inline instead of queuing. |
| `run_agent.py` | `_pending_steer` state + `steer()`, `_drain_pending_steer()`, `_apply_pending_steer_to_tool_results()`. Drain hook at end of both parallel and sequential tool executors. Cleared by `clear_interrupt()`. Leftover steer surfaces in `run_conversation` result as `pending_steer`. |
| `cli.py` | `/steer` handler — calls `agent.steer()` when running, falls back to `_pending_input` otherwise. Consumes `result["pending_steer"]` between turns. |
| `gateway/run.py` | Running-agent intercept calls `running_agent.steer(text)`; idle path strips the slash prefix and forwards as a regular user message. Sentinel/missing-method fallbacks route to `/queue` semantics. |
| `tui_gateway/server.py` | New `session.steer` JSON-RPC method. |
| `ui-tui/src/app/slash/commands/core.ts` | `/steer` slash command — `session.steer` when `ui.busy`, otherwise `composer.enqueue`. |
| `ui-tui/src/gatewayTypes.ts` | `SessionSteerResponse` type. |

## Fallbacks

| Situation | Behavior |
|---|---|
| Agent exits before another tool batch | Leftover surfaces as `result["pending_steer"]`; CLI/gateway deliver as next user turn (never silently dropped). |
| All tools skipped after interrupt | Re-stashes the steer so the fallback path can pick it up. |
| `clear_interrupt()` called | Pending steer is dropped — the agent's next iteration won't happen, so late delivery would surprise the user. |
| No active agent | `/steer` reduces to sending the text as a normal message. |
| Multiple `/steer`s during one batch | Concatenated with newlines; delivered together. |
| Anthropic-style list content in tool result | Steer appended as a new text block, existing blocks preserved. |

## Validation

| | Before | After |
|---|---|---|
| Mid-run user nudges | `/queue` waits until agent completes the whole run | `/steer` arrives on the next tool-call boundary |
| Role alternation invariant | N/A | Preserved (only modifies an existing tool-role message) |
| Prompt cache | N/A | No additional invalidation beyond normal per-turn tool-result churn |
| Targeted tests | | 72/72 pass under `scripts/run_tests.sh` |

### Test coverage

- `tests/run_agent/test_steer.py` (18) — accept/reject, concatenation, drain, last-tool-result injection, multimodal list content, thread safety, cleared-on-interrupt, registry + bypass-set membership.
- `tests/gateway/test_steer_command.py` (5) — running agent, pending sentinel, missing `steer()` method, rejected payload, empty payload.
- `tests/gateway/test_command_bypass_active_session.py` (+1) — `/steer` bypasses the Level‑1 active-session guard.
- `tests/test_tui_gateway_server.py` (+3) — `session.steer` RPC: queued path, empty-text rejection, agent-without-steer error.

## Not in t

…(truncated)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_command_bypass_active_session.py`
- `tests/gateway/test_steer_command.py`
- `tests/run_agent/test_steer.py`
- `tests/test_tui_gateway_server.py`