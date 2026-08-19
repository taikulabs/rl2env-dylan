**fix(compression): include system prompt + tool schemas in token estimates**

Auto-compression banners and the post-compression `last_prompt_tokens` writeback now report real request pressure instead of a transcript-only char/4 estimate — which was missing the system prompt and tool schemas and could underestimate by 200x+ on sessions with many tools.

## Root cause
`estimate_messages_tokens_rough(messages)` only counts `sum(len(str(msg)) for msg in messages) / 4`. With a 15KB system prompt and 30 tool schemas (~26KB), a 4-message transcript that looks like **45 tokens** to that estimator is really **~10,550 tokens** of real request pressure — a **234x** gap.

## User-facing symptoms this closes

**#6217** (reported by @Jackten) — `/compress` banner shows compression triggering at a tiny number like ~4,462 tokens even though the real pressure is much higher, and can even report the post-compression count as larger than the pre-compression count because a dense handoff summary replaces many short turns. Also reported by @codecovenant on X (2026-04-30) as the trigger for this PR: 'tells you its happening at a number much lower than threshold.'

**#14695** (reported by @devilardis) — `last_prompt_tokens` writeback after `_compress_context()` omits tool schemas, so the next `should_compress()` check compares real usage against a stale underestimate. Compression triggers late and can exceed the model's context limit on small-context models.

## Fix
Swap `estimate_messages_tokens_rough()` → `estimate_request_tokens_rough(messages, system_prompt=..., tools=...)` everywhere a user-visible number is shown or the compressor's internal tracking is updated. The correct estimator already existed for exactly this purpose.

## Changes
- `run_agent.py` — post-compression `last_prompt_tokens` writeback (); post-tool-call `should_compress()` fallback when provider usage is missing
- `cli.py` — `/compress` banner + before/after summary
- `gateway/run.py` — gateway `/compress` banner + summary
- `tui_gateway/server.py` — TUI `/compress` status line + summary
- `acp_adapter/server.py` — ACP `/compact` before/after
- `agent/manual_compression_feedback.py` — relabel 'Rough transcript estimate' → 'Approx request size' (the metric changed)

## Intentionally NOT changed
- Session-hygiene fallback and the 'no agent' `/status` fallback in `gateway/run.py` — no agent is in scope to query for system prompt / tools, and the existing 30–50% overestimate wobble in hygiene is safety-accepted (see comment at gateway/run.py:5582).
- Verbose-mode `Request size` logging — `api_messages` already contains the system prompt in index 0, so it's not user-visible-misleading.

## Validation
E2E with realistic fixture (15KB system prompt, 30 tool schemas, 4 short messages):

| | Before fix | After fix |
|---|---|---|
| `/compress` banner shows | `~45 tokens` | `~10,552 tokens` |
| Post-compression `last_prompt_tokens` | 75,000 | 105,000 |
| `should_compress()` at 100K threshold | `False` (delayed) | `True` (on time) |

Targeted tests — all passing on this branch:
- `tests/cli/test_manual_compress.py` — 4/4
- `tests/gateway/test_compress_command.py` — 4/4
- `tests/test_cli_manual_compress.py` — 1/1
- `tests/acp/test_server.py::test_compact_compresses_context` — pass
- `tests/tui_gateway/` — 189/189
- `tests/agent/test_context_compressor.py` + friends — 115/115

The 2 pre-existing failures in `tests/acp/test_server.py::test_send_available_commands_update` and `tests/run_agent/test_concurrent_interrupt.py` also fail on clean `origin/main` — unrelated.

## Credits
- Diagnosis in #14695 by @devilardis
- Diagnosis in #6217 by @Jackten
- Report via X by @codecovenant