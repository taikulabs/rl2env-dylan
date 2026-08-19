**fix(gateway): route plain-text approval responses (salvage #46924)**

## Summary
Replying "yes" / "approve" / "deny" (plain text, no slash) now resolves a pending dangerous-command approval on messaging platforms — previously it deadlocked into an auto-deny.

Root cause: when the agent is blocked inside `tools/approval.py` waiting for approval, a bare-word reply fell through to the steer/queue/interrupt logic in `_handle_active_session_busy_message`. The reply got queued behind a turn that can't start until the approval resolves, so the approval timed out and auto-denied. Slash forms (`/approve`, `/deny`) already worked; bare words (what Signal/SMS users naturally type) did not.

Salvage of @liuhao1024's #46924 — their commit's authorship is preserved. Our follow-up commit reuses the canonical handlers and delivers the confirmation reply.

## Changes
- `gateway/run.py`: in `_handle_active_session_busy_message`, when `has_blocking_approval(session_key)` is true, route bare-word approval vocab (`yes`/`approve`/`ok`/`y`/`confirm`/`deny`/`no`/`reject`/`cancel`/`n`/`always`/`session`) through the existing `/approve` and `/deny` handlers — which resolve the waiting thread, resume typing, and return a localized confirmation — then deliver that confirmation to the user (it was silent before). Synthesizes a literal `/`-prefixed command so `get_command_args()` parses `always`/`session` on every platform (`is_command()` only recognizes `/`).
- `tests/gateway/test_plaintext_approval_routing.py`: E2E tests over the real busy-handler path.

## Why this location is correct
The base-adapter guard (`gateway/platforms/base.py`) invokes the busy-session handler before falling back to queueing, so plain text does reach this handler. The fix sits before the steer/queue logic and after the early-return guards (draining, internal synthetic events). The `has_blocking_approval` gate is the disambiguator — a conversational "yes" with no pending approval is never treated as command approval (preserving the design intent at `run.py`'s "Pending exec approvals are handled by /approve and /deny" note).

## Validation
| | Before | After |
|---|---|---|
| Signal/SMS reply "yes" to approve | queued → timeout → auto-deny | resolves approval, command runs |
| User feedback after plain-text reply | silent | localized confirmation sent |
| `always` / `session` modifiers | not parsed | parsed via synthesized `/approve <arg>` |
| Conversational "yes" (no approval pending) | n/a | not consumed as approval |

14 E2E tests green; adjacent approval/busy suites (`test_approve_deny_commands.py`, `test_busy_session_ack.py`) pass with no regressions.

## Infographic

![PR #46924 plain-text approval routing](https://v3b.fal.media/files/b/0aa06ad8/OVZErZ9kP0YmgdL6-BaVS_C4h3Kt4k.png)

.