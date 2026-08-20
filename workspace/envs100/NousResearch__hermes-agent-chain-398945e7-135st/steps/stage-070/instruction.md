**feat: /goal — persistent cross-turn goals (Ralph loop)**

## Summary

Adds `/goal <text>`, a standing-goal slash command that keeps Hermes working toward a stated objective across turns until it is achieved, paused, or the turn budget runs out.

**Inspiration / prior art:** our take on the Ralph loop, directly inspired by [Codex CLI 0.128.0's `/goal`](https://github.com/openai/codex) — built by [Eric Traut](https://github.com/erictraut) (Pyright) on the Codex team. Same core idea (keep the goal alive across turns, don't stop until it's achieved); implementation is independent and adapted to Hermes' architecture (central `CommandDef` registry, `SessionDB.state_meta` persistence, auxiliary-client judge, adapter-FIFO continuation on gateway).

After each turn, an auxiliary-model judge call asks 'is this goal satisfied by the assistant's last response?'. If not, Hermes feeds a continuation prompt back into the same session as a normal user turn. Any real user message preempts the loop automatically. Judge failures fail OPEN (continue) so a flaky judge can never wedge progress — the turn budget (default 20) is the real backstop.

## Commands

| | |
|---|---|
| `/goal <text>` | Set standing goal (kicks off first turn immediately) |
| `/goal` or `/goal status` | Show current state |
| `/goal pause` | Pause the continuation loop |
| `/goal resume` | Resume (resets turn counter) |
| `/goal clear` | Drop the goal |

Works identically on CLI and gateway via the central `CommandDef` registry.

## Design invariants preserved

- **Prompt cache** — continuation prompts are regular user-role messages appended to history. No system-prompt mutation, no toolset swap.
- **Role alternation** — continuation is a user turn, never injected mid-tool-loop.
- **Session persistence** — goal state lives in `SessionDB.state_meta` keyed by `goal:<session_id>`, so `/resume` picks it up.
- **Mid-run safety** — on the gateway, `/goal status|pause|clear` are allowed mid-run (control-plane only); setting a new goal requires `/stop` first so we don't race a second continuation prompt against the current turn.
- **Any-message preemption** — on CLI, goal continuations go through `_pending_input` so a real user message queued during the judge call runs first. On gateway, they go through the adapter FIFO with the same effect.

## Files

- `hermes_cli/goals.py` (new) — `GoalManager` + `judge_goal` + `GoalState`
- `hermes_cli/commands.py` — CommandDef entry (one line)
- `hermes_cli/config.py` — `goals.max_turns: 20` default
- `hermes_cli/web_server.py` — dashboard category merge (goals → agent)
- `cli.py` — `_handle_goal_command` + `_maybe_continue_goal_after_turn` hook in process_loop
- `gateway/run.py` — `_handle_goal_command` + `_post_turn_goal_continuation` wrapping `_handle_message_with_agent`
- `tests/hermes_cli/test_goals.py` (new, 26 tests)
- `website/docs/reference/slash-commands.md`

## Validation

| | |
|---|---|
| Targeted tests | 26/26 in `tests/hermes_cli/test_goals.py` |
| Broader `tests/hermes_cli/` | 3519 passed (1 pre-existing copilot-auth flake, unrelated) |
| `tests/gateway/` | 4407 passed (1 pre-existing `test_teams.py` plugin flake, unrelated) |
| `tests/hermes_cli/test_web_server.py` | Fixed `test_no_single_field_categories` (merged `goals → agent` in dashboard) |
| Live test 1 — judge round-trip | `done` / `continue` / `continue` (empty) / `continue` (partial) — all correct, 2-7s latency |
| Live test 2 — real CLI loop | Goal "print hello, Ralph loop" — turn 1 judge caught ambiguity ('didn't confirm terminal output'), turn 2 agent re-ran with confirmation, judge said done, loop halted cleanly |
| Live test 3 — budget exhaustion | 4-file goal with `max_turns=2` → paused at 2/2 turns with correct `/goal resume` message, zero runaway |

## Notes

- `goals.max_turns` is the only config knob for now. Kept minimal — adding more keys without concrete need would be speculative.
- Judge uses `get_text_auxiliary_client("goal_judge")` so users can route it to a cheap model via the `auxiliary.goal_judge` config ov

…(truncated)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_goals.py`