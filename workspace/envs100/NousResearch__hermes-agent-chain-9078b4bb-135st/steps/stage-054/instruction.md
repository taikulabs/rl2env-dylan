**fix(dashboard): show live session title in /chat header**

The dashboard `/chat` header now shows the live session title instead of the static "Chat" route label.

Salvages #50549 by @shannonsands onto current `main` (cherry-picked, authorship preserved).

## Why
Resumed sessions already carry persisted titles, and auto-title / manual `/title` updates can arrive after the page loads — but the dashboard header was wired to neither source, so it stayed stuck on the route label "Chat".

## Changes
- `tui_gateway/server.py`: add `title` to the `_session_info` payload (reuses the existing `_session_live_title()` helper) and emit a fresh `session.info` whenever `/title` resolves a session title.
- `web/src/components/ChatSidebar.tsx`: forward `session.info` title updates via a new `onSessionTitleChange` callback.
- `web/src/pages/ChatPage.tsx`: seed the header from resumed-session metadata (`getSessionDetail`) and update it from live title events; `titleScope` keys on `reconnectNonce` so a fresh-session bump discards a stale title.
- `web/src/lib/chat-title.ts`: small title-normalization helper + unit tests.
- `web/src/lib/api.ts`: `getSessionDetail()` reading the existing `/api/sessions/{id}` endpoint.

## Validation
| Check | Result |
|---|---|
| `pytest tests/test_tui_gateway_server.py -k 'session_title or session_info_includes_session_title or set_session_title'` | 11 passed |
| `vitest run src/lib/chat-title.test.ts` | 5 passed |
| `npm run typecheck --workspace web` | clean |

## Infographic

![dashboard-chat-titles](https://v3b.fal.media/files/b/0a9f4489/xf8tsXk6lDNCOhh7PGkrj_ypK5CF0U.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_tui_gateway_server.py`
- `web/src/lib/chat-title.test.ts`