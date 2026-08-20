**feat(discord): forum channel support (salvage of #10145 + media + polish)**

Discord forum channels (type 15) now accept `send_message`, TTS, images, voice, and file attachments — previously silent-failed on every outbound call.

Salvages #10145 (ChimingLiu's forum channel support) onto current main and extends media handling on both the REST and websocket paths.

## Changes
- `tools/send_message_tool._send_discord`: forum thread creation now uploads media files as multipart attachments on the starter message in a single call. Previously media files were silently dropped on the forum path.
- `gateway/platforms/discord.DiscordAdapter`:
  - New `_forum_post_file` helper: creates a thread with the file as starter content.
  - `_send_file_attachment`, `send_voice`, `send_image`, `send_animation` route forum sends through the helper instead of `channel.send(file=...)` (which forums reject).
  - `_send_to_forum` collects per-chunk follow-up failures into `raw_response['warnings']`.
- `tools/send_message_tool`: process-local `_DISCORD_CHANNEL_TYPE_PROBE_CACHE` memoizes `GET /channels/{id}` probes — avoids a roundtrip on every send when the directory cache has no entry.
- `gateway/channel_directory`: enumerate forum channels (type 15) + new `lookup_channel_type()` helper (ChimingLiu).
- Docs: new Forum Channels section in `website/docs/user-guide/messaging/discord.md`.

## Validation
| | Before | After |
|---|---|---|
| Text-only send to forum | Silent fail on REST; works on websocket | Works on both paths |
| `send_message` with media to forum | Media silently dropped | Multipart upload on starter message |
| `send_voice` / image / video / document to forum | `channel.send(file=...)` → rejected | Thread created with file as starter |
| Uncached channel, repeat sends | `GET /channels/{id}` on every send | Probed once, memoized |
| Targeted test suite | 86 existing | 117 passing (22 new) |

## Credit
Original PR: @ChimingLiu — #10145. Commit authorship preserved on the salvaged commit (`git log`).

.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_discord_send.py`
- `tests/tools/test_send_message_tool.py`