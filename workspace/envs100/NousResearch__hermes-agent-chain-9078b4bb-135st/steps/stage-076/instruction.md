**feat(goals): completion contracts for /goal — evidence-based judging**

## Summary
`/goal` can now carry a structured **completion contract** so "done" is decided against evidence instead of vibes — the highest-leverage idea from OpenAI Codex's `/goal` guidance, adapted onto our existing (deeper) goal loop.

A bare `/goal <text>` behaves exactly as before. Optionally, a goal gains five contract fields — **outcome / verification / constraints / boundaries / stop_when**. When set, the continuation prompt tells the agent to target the verification surface and respect constraints, and the judge marks the goal `done` only when the verification criterion is met with **concrete evidence** (command result, file excerpt, test output). This directly tightens the most common `/goal` failure mode: premature completion or endless over-continuation on an underspecified objective.

## Two ways to set a contract (both backward compatible)
- **`/goal draft <objective>`** — expands a plain-language one-liner into a full contract via the `goal_judge` aux model (cache-safe side call, main-model-first). Falls back to a free-form goal if the model is unavailable — drafting never blocks setting a goal. (Codex's "let the agent draft the goal" tip.)
- **`/goal <text>` with inline `field: value` lines** (`verify:`, `constraints:`, `boundaries:`, `stop when:`, …). The first non-field line is the headline; only known field prefixes are pulled out, so a plain goal with an incidental colon (`Fix bug: the parser…`) is not mangled.
- **`/goal show`** prints the active contract.

Contracts persist in `SessionDB.state_meta` alongside the goal (survive `/resume`), compose with `/subgoal` criteria (subgoals fold in as extra criteria the judge must also satisfy), and old goal rows load unchanged.

## Changes
- `hermes_cli/goals.py`: `GoalContract` dataclass + `parse_contract()` (inline parser) + `draft_contract()` (aux-model expander) + contract-aware continuation/judge prompt templates; `GoalState.contract` field with backward-compatible serialization; `GoalManager.set(contract=…)`, `set_contract()`, `has_contract()`, `render_contract()`; judge threads the contract through.
- `hermes_cli/cli_commands_mixin.py`: `/goal draft`, `/goal show`, inline-contract parsing in `_handle_goal_command`.
- `gateway/slash_commands.py`: same surface for every gateway platform (`draft` aux call runs in an executor).
- `hermes_cli/commands.py`: updated `/goal` args hint.
- `website/docs/user-guide/features/goals.md`: Completion contracts section.

Zero new model tools — all surfaces call the shared `GoalManager` engine. No prompt-cache invalidation (continuation is still a plain user-role message; the contract just enriches its text).

## Validation
| | Result |
|---|---|
| `tests/hermes_cli/test_goals.py` | 73/73 (+18 new: parse/serialize/judge-prompt/draft/fallback) |
| broader goal surface (CLI/gateway/TUI/kanban/compression) | 42/42, 0 regressions |
| `tests/hermes_cli/test_commands.py` | 156/156 |
| Live E2E | set contract → persist → reload (fresh manager) → contract-aware continuation+judge prompts → legacy row loads clean → plain goal unaffected, all green |
| ruff | clean on all 4 Python files |

## Attribution
Builds on Hermes' existing `/goal` (our Ralph-loop take). The completion-contract concept is adapted from OpenAI Codex's `/goal` use-case + cookbook guidance; the implementation is independent and layered onto our `GoalManager`/`SessionDB` architecture.

## Infographic

![completion-contracts-for-goal](https://v3b.fal.media/files/b/0a9f4131/I1AIhqar_X2uK81uQOhi2_8pybMoLE.png)