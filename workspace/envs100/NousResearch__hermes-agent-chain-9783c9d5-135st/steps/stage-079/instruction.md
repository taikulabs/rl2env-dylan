**fix: URL-encode Signal phone numbers and correct attachment RPC parameter**

## Summary
- **SSE connection fix**: Phone numbers containing `+` (E.164 format like `+31612345678`) were passed raw into the SSE query string. The `+` was interpreted as a space by the HTTP server, causing `400 Bad Request` errors and breaking all inbound message reception. Fix: `quote(self.account, safe='')` encodes `+` as `%2B`.
- **Attachment download fix**: The `getAttachment` JSON-RPC call used parameter name `attachmentId`, but signal-cli expects `id`. This caused a `NullPointerException` in signal-cli, silently failing all attachment downloads (images, documents, audio). Fix: rename parameter to `id`.

Both bugs were reported by a user whose Signal interactions were broken on every upstream update because the fixes kept getting overwritten.