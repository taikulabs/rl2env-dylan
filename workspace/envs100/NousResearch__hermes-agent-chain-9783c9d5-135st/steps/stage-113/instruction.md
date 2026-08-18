**fix(matrix): E2EE decryption — request keys, auto-trust devices, retry buffered events**

## Summary

When the Matrix adapter receives encrypted events it can't decrypt (`MegolmEvent`), it previously just logged a warning and dropped the message. This PR adds four mechanisms to fix decryption failures in encrypted rooms:

### Changes

**1. Room key requests** — When a `MegolmEvent` arrives (failed decrypt), the bot now calls `client.request_room_key(event)` to ask other devices in the room to forward the missing session key.

**2. Auto-trust devices** — After each `keys_query()`, the bot auto-verifies all unverified devices in the device store. This makes senders' clients share Megolm session keys with us proactively. Without this, many Matrix clients refuse to include an unverified device in key distributions.

**3. Retry buffer** — Undecrypted events are buffered (bounded to 100 events, 5 minute TTL) and retried after each E2EE maintenance cycle. When new keys arrive (from key requests, key queries, or to-device forwarding), the bot re-attempts decryption and routes successfully decrypted events to the appropriate handler (text or media).

**4. Key export/import** — Megolm keys are exported to a file on disconnect and imported on connect, so session keys survive gateway restarts. This prevents the loss of decryption capability for existing room sessions across restarts.