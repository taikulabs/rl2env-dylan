**docs(sessions): clarify sessions.json is the gateway routing index, not the session list**

## Summary
`sessions.json` is now self-documenting, so users stop mistaking the gateway routing index for the session list.

Issue #49361 reported CLI sessions as "invisible": the user inspected `~/.hermes/sessions/sessions.json`, saw only `agent:main:whatsapp:dm:...` entries, and concluded their CLI sessions were lost. But `sessions.json` is the **gateway routing index** (session-key → active session ID) — it only ever holds gateway/messaging entries. `hermes sessions list`, `/sessions`, and the dashboard all read `state.db`, which holds every session (CLI, TUI, gateway). The reported "bug" is a wrong-store misdiagnosis; this PR closes the UX gap that caused it.

## Changes
- `gateway/session.py`: write a self-documenting `_README` sentinel at the top of `sessions.json` explaining it's the gateway routing index and that all sessions live in `state.db` (shown by `hermes sessions list`). Skip `_`-prefixed keys on load so the sentinel never round-trips into a `SessionEntry`.
- Harden every `sessions.json` reader against the sentinel so a string-valued key can't `AttributeError` an `entry.get(...)` call: `mcp_serve._load_sessions_index`, `gateway/mirror.py`, `gateway/channel_directory.py`.
- `website/docs/user-guide/sessions.md`: a `:::warning` callout naming the exact symptom from the report, pointing at `state.db` / `hermes sessions repair`.
- Tests: prune assertion now ignores metadata sentinels; new round-trip coverage that the sentinel is written first, skipped on load, and real entries survive intact.

## Validation
| | Before | After |
|---|---|---|
| `cat sessions.json` | opaque whatsapp-only dict, no explanation | leads with `_README` explaining it's the routing index + where sessions actually live |
| sentinel on load | n/a | skipped, never becomes a `SessionEntry` |
| all `sessions.json` readers | would crash on a string sentinel | skip `_`-prefixed keys |
| affected test files | — | 247 passed, 0 failed |

E2E-verified against real imports + a temp `HERMES_HOME`: SessionStore save/load round-trip, plus `mcp_serve`, `mirror._find_session_id`, and `channel_directory._build_from_sessions` all skip the sentinel and still resolve the real whatsapp entry.

 (as a UX/docs fix — the index itself was working as designed).

## Infographic

![sessions-json-self-documenting](https://v3b.fal.media/files/b/0a9f8c67/TlKTjlTa0sFaTkS8pVFLa_JR8vsTYs.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_session_store_prune.py`