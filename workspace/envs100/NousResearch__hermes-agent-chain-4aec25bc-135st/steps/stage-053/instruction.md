**feat(gateway): deliverable mode — ship artifacts as native uploads from any agent surface**

## Summary

Agent can now ship arbitrary deliverables — charts, PDFs, spreadsheets, generated images, archives — as native attachments in Slack, Discord, Telegram, etc., just by referencing the absolute path in its response. Same primitive flows through kanban: workers attach artifacts to `kanban_complete`, the gateway notifier uploads them alongside the completion message.

This is the Hermes-side answer to "what does Perplexity Computer's Slack integration do that we don't?" — closes ~70% of the visible gap.

## Changes

- `gateway/platforms/base.py` — `extract_local_files` extension list expanded from `(png/jpg/.../mp4)` to cover PDFs, docx, csv/xlsx/json/yaml, pptx, zip/tar/gz, mp3/wav, html. Image/video still embed inline; everything else routes to `send_document` via the existing dispatch in `gateway/run.py`.
- `tools/kanban_tools.py` — `kanban_complete` gains an `artifacts: list[str]` parameter. Handler stashes the list in `metadata["artifacts"]`; bare-string is auto-promoted; merges with any pre-existing `metadata.artifacts` without dupes.
- `hermes_cli/kanban_db.py` — completed-event payload now carries `artifacts` (promoted from metadata) so the notifier finds them without a second SQL round-trip.
- `gateway/run.py` — `_kanban_notifier_watcher` now calls a new `_deliver_kanban_artifacts` helper after sending the completion text. Helper reads `payload.artifacts` (preferred), falls back to scanning the summary + `task.result` with `extract_local_files`, then partitions images / videos / documents and uploads via `send_multiple_images` / `send_video` / `send_document`.
- `website/docs/user-guide/features/deliverable-mode.md` + `sidebars.ts` — user-facing docs page covering the extension list, the kanban artifacts pattern, and a recommended MCP servers list for connector breadth.

## Validation

| Test target | Result |
|---|---|
| Authored tests (extract, kanban_complete artifacts, notifier upload) | 13 new cases, all pass |
| `tests/gateway/test_extract_local_files.py` | 44/44 |
| `tests/tools/test_kanban_tools.py` | 17/17 (4 new) |
| `tests/hermes_cli/test_kanban_notify.py` | 12/12 (2 new) |
| `tests/gateway/` + `tests/hermes_cli/test_kanban_*` together | 5690 passed, 7 pre-existing skips, 0 regressions |
| E2E with real files + real kanban kernel + real BasePlatformAdapter | passes (`kanban_complete(artifacts=[png,pdf,csv])` → metadata + event payload land → notifier partitions correctly → send_multiple_images called with PNG, send_document called twice with PDF + CSV) |

## Not in this PR (deferred)

- **Ad-hoc "research for two hours, ping me when done" slash command.** Already covered by `kanban_create` + `kanban_subscribe`. A dedicated slash command can ride a follow-up PR if there's demand.
- **Setup-wizard prompt for recommended MCP servers** (Notion / GitHub / Linear / Slack / Gmail / Salesforce / Snowflake / Drive). Listed in the new docs page; UI integration is a separate change.

## Backwards compatibility

- `extract_local_files` is additive — every old test for image / video extensions still passes; only `test_no_media_extensions` needed updating (it was a snapshot of the old narrow extension list).
- `kanban_complete` `artifacts` parameter is optional. Workers that don't pass it behave identically.
- No agent-loop changes. No system-prompt changes. No prompt-cache impact.
- Existing `MEDIA:<path>` tag path is untouched; bare-path delivery is the simpler primitive that small models can use without the tag syntax.

## Plan reference

Full rationale, comparison to Perplexity Computer, and discussion of what's deliberately *not* matched (Firecracker microVMs, hosted token storage, 400-connector catalog) lives in `~/.hermes/docs/perplexity-computer-parity.pdf` (local).