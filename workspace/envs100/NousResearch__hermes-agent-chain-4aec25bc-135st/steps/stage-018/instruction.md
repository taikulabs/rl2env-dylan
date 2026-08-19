**feat(cli): add /exit --delete flag to remove session on quit (salvage of #17665)**

## Summary
Salvage of #17665 — `/exit --delete` (also `/quit --delete`, `-d`) removes the current session's SQLite row and on-disk transcripts during shutdown. Useful for privacy-sensitive workflows. Port from google-gemini/.

No new SQL or filesystem code — the `SessionDB.delete_session(session_id, sessions_dir=...)` API already existed for `hermes sessions delete` and handles SQLite removal (orphans child sessions to satisfy FK constraints) + `.json` / `.jsonl` / `request_dump_*` cleanup. This PR wires it into the `/exit` slash command.

## Salvage notes
Branch was 1,823 commits stale. Two conflicts:
- `cli.py`: main changed `("quit", "exit", "q")` to `{"quit", "exit"}` (set, dropped the `q` alias to avoid colliding with `/queue`). Kept main's form, applied PR's `--delete` parsing on top.
- `slash-commands.md`: kept PR's expanded `/quit` description.

## Changes
- `cli.py` (+15): new `_delete_session_on_exit` one-shot flag; `process_command()` parses `--delete`/`-d` after `/exit` or `/quit` and arms it; unknown args print a hint and keep the CLI running (so typos like `/exit -delete` don't accidentally exit). Shutdown path calls `SessionDB.delete_session(sid, sessions_dir=...)` after `end_session()` when armed.
- `hermes_cli/commands.py` (+1): `/quit` CommandDef gains `args_hint="[--delete]"` so `/help` and autocomplete surface the flag.
- `tests/cli/test_exit_delete_session.py` (+128): 12 cases — both aliases, case insensitivity, whitespace, short form, unknown-arg rejection, registry metadata.
- `website/docs/reference/slash-commands.md` (+1): `/quit` row mentions `--delete`.

## Validation
| | Result |
|---|---|
| New tests + commands registry | 154/154 |
| `tests/cli/` (regression) | 706/706 |
| E2E (isolated HERMES_HOME, real `SessionDB` + on-disk artifacts) | DB row + 3 files deleted; idempotent re-delete returns False |

## Source
google-gemini/. Originally scouted in #17665.