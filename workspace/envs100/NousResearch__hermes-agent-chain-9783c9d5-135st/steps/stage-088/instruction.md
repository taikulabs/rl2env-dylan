**fix(whatsapp): reuse persistent aiohttp session across requests**

## Summary

Standardizes the WhatsApp adapter to use a persistent `aiohttp.ClientSession` like the Mattermost, HomeAssistant, and SMS adapters already do. Also adds explicit poll task cancellation on disconnect.

Salvaged from PR #1851 by Himess (March 18). The `_poll_task` storage was already on main from PR #3267; this adds the disconnect cancellation and the persistent session.

## Changes

- Create `self._http_session` in `connect()`, close in `disconnect()`
- All 6 bridge HTTP methods (`send`, `edit_message`, `_send_media_to_bridge`, `send_typing`, `get_chat_info`, `_poll_messages`) use the shared session
- Explicitly cancel `_poll_task` on `disconnect()` (previously relied on `self._running = False` with a race window)
- Health-check sessions in `connect()` remain ephemeral
- Removed per-method `ImportError` guards for aiohttp (always available via `[messaging]` extras)

## Tests

4 new tests in `TestHttpSessionLifecycle`:
- Session closed on disconnect
- Session skip when already closed
- Poll task cancelled on disconnect
- Done poll task not cancelled

All 19 WhatsApp tests passing.