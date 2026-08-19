**feat(skills): /learn — distill a reusable skill from anything you describe**

## Summary
`/learn <anything>` distills a reusable skill from whatever you describe — a directory, a URL, the workflow you just walked the agent through, or pasted notes — and saves it following the house authoring standards.

Open-ended and engine-free: `/learn` builds a standards-guided prompt and hands it to the live agent as a normal turn. The agent gathers the sources with the tools it already has (`read_file`/`search_files` for dirs, `web_extract` for URLs, the current conversation for "what I just did", the pasted text as-is) and authors the `SKILL.md` via `skill_manage`. No distillation engine, **no model-tool footprint**, and it works identically on local, Docker, and remote terminal backends because there is no host-side ingestion step.

This supersedes #47234 (a directory-only distillation engine with a `/learn` command + dashboard endpoint). Per review, the engine was dropped in favor of the open-ended agent-driven design: making `/learn` open-ended means dirs/URLs/conversation/paste all "just work" through the agent's existing tools, with zero new surface. Inspired by OpenAI Codex's "Record & Replay" (learn-by-demonstration) — the agent's own session is the demonstration.

## How it works (one path, every surface)
- **`/learn` (CLI)** — injects the standards-guided prompt onto the agent input queue (same mechanism as skill slash commands).
- **`/learn` (gateway)** — rewrites the turn to the prompt and falls through to agent processing (the `/blueprint` pattern; preserves role alternation).
- **`/learn` (TUI + dashboard chat + desktop)** — `command.dispatch` returns a `send` directive carrying the prompt.
- **Dashboard Skills page** — a **Learn a skill** button opens a panel with a directory field, a URL field, and an open-ended text box; it composes a `/learn` request and runs it in chat (`?learn=` → ChatPage types it into the PTY composer once booted).

The authoring standards (description ≤60 chars, the modern section order, Hermes-tool framing, no invented commands, scripts in `scripts/`) are baked into the prompt in `agent/learn_prompt.py`, distilled from AGENTS.md's "Skill authoring standards (HARDLINE)".

## Changes
- `agent/learn_prompt.py` (new): shared standards-guided prompt builder.
- `hermes_cli/commands.py`: `/learn` registry entry (both surfaces, Tools & Skills).
- `hermes_cli/cli_commands_mixin.py`: CLI `_handle_learn_command` (inject onto input queue).
- `gateway/run.py`: gateway `/learn` (rewrite turn + ack, fall through).
- `tui_gateway/server.py`: `command.dispatch` returns a `send` directive for `/learn`.
- `web/src/pages/SkillsPage.tsx`: "Learn a skill" panel (dir + URL + open-ended text).
- `web/src/pages/ChatPage.tsx`: one-shot `?learn=` → type the `/learn` command into the composer on PTY open.
- `website/docs/`: slash-commands reference + skills feature page section.
- `tests/agent/test_learn_prompt.py` (new): 11 tests.

## Validation
- 11/11 new tests pass; `tests/hermes_cli/test_commands.py` 156/156 and `tests/gateway/test_gateway_command_help.py` 4/4 still green.
- E2E (real imports, temp `HERMES_HOME`): prompt builder embeds the request + standards + `skill_manage`; empty input falls back to the conversation; registry resolves `/learn` on both surfaces and in autocomplete; `command.dispatch` yields the `send` directive.
- `py_compile` clean on all 6 touched Python files; `ruff check` clean; `web` `tsc --noEmit` clean.