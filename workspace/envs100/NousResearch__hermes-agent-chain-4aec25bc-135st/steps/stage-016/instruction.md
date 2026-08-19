**fix(signal): read groupV2.id in envelope, fall back to legacy groupInfo (salvage of #16260)**

## Summary
Salvage of #16260 — modern Signal V2-only groups arrive on `dataMessage.groupV2.id`, not `groupInfo.groupId`. Without this read they're misrouted as DMs to the sender. Port from qwibitai/.

## Why
signal-cli's JSON-RPC envelope shape has drifted across versions: some forward the underlying libsignal V2 envelope verbatim (`groupV2`), others normalize everything into `groupInfo`. Hermes only read `groupInfo`, so V2-only groups had `group_id = None` and fell through to the DM path.

## Changes
- `gateway/platforms/signal.py`: read `dataMessage.groupV2.id` first, fall back to `dataMessage.groupInfo.groupId`. Add `isinstance(..., dict)` guards on both fields plus the `chat_name` extraction so malformed envelopes don't crash with `AttributeError`.
- `tests/gateway/test_signal.py`: 6 new tests in `TestSignalGroupV2Routing` covering V2 routing, V1 legacy fallback, V2-preferred precedence when both fields are present, no-group DM path, allowlist enforcement on V2 ids, malformed payloads.

## Salvage note
Branch was 2,419 commits stale. One test-file conflict — both main and the PR appended new test classes at end-of-file; both kept.

## Validation
| | Result |
|---|---|
| `tests/gateway/test_signal.py` | 109/109 (67 on pre-PR main + 36 main-added + 6 PR-added) |

## Source
qwibitai/. Originally scouted in #16260.