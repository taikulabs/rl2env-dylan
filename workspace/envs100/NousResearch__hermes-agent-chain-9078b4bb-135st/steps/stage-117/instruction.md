**fix(matrix): use member_count as DM signal for named DM rooms**

Matrix DM rooms with client-assigned names are now correctly classified as DMs instead of rooms, so require_mention no longer fires in legitimate one-on-one DMs.

## Root cause
`_resolve_room_identity()` used `chat_type = "dm" if is_direct and not has_explicit_name else "room"`. That `not has_explicit_name` check was added () to defend against stale `m.direct` entries for rooms that later became groups. But most Matrix clients (Element, SchildiChat, FluffyChat, …) auto-set a room name when creating a DM ("Alice & Bot"), so `has_explicit_name` is almost always true and virtually every client-created DM was misclassified as `room`.

## Fix
`member_count` becomes the primary DM signal: `<=2` members means the room is necessarily a 1:1 conversation, regardless of `m.direct` or an explicit name. Falls back to the old `m.direct + name` heuristic only when the count is unavailable. A room that grew to 3+ members but is still in stale `m.direct` is still classified as a room (and the `conflict` flag is set). Also hardens `_get_room_member_count` with a `joined_members` API fallback when the cache-backed `state_store` is empty.

## Changes
- `plugins/platforms/matrix/adapter.py`: member-count-primary classification in `_resolve_room_identity`; two-tier `_get_room_member_count` (state_store → API).
- `tests/gateway/test_matrix.py`: named 2-member room → DM; new named-DM-in-m.direct case; stale-m.direct case bumped to 3 members → room.
- `tests/gateway/test_matrix_project_context_isolation.py`: pin member_count=3 for the synthetic-thread room so it stays a room.

## Validation
| Scenario | Before | After |
|---|---|---|
| Named DM (≤2 members, in m.direct) | room (mention required) | **dm** |
| Named 2-member room (not in m.direct) | room | **dm** |
| Stale m.direct, grew to 3+ members | room | room (unchanged) |
| Pure group chat (not in m.direct) | room | room (unchanged) |
| member_count unavailable | falls back to name heuristic | falls back (unchanged) |

`scripts/run_tests.sh tests/gateway/test_matrix.py tests/gateway/test_matrix_project_context_isolation.py tests/gateway/test_matrix_mention.py` → all pass (250 + mention).

## Credit
Salvaged from #48554 by @justemu (the original reporter, earliest fix) onto the current plugin adapter path — the Matrix adapter moved from `gateway/platforms/matrix.py` to `plugins/platforms/matrix/adapter.py` since the PR was opened, so it couldn't cherry-pick cleanly. Authorship preserved.

. Supersedes #48554 and #48753.

## Infographic

![matrix-dm-classification-fix](https://v3b.fal.media/files/b/0a9f8c89/2c1PNrfWDF5PFCHLIcVVg_IrY9cc8p.png)