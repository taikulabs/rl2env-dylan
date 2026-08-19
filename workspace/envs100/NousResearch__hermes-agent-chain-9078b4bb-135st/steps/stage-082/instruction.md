**fix(gateway): redact credentials from TUI approval prompts (#48456 follow-up)**

## Summary

 — completes the whole-bug-class fix for **#48456**.

#50767 redacted credentials from two approval-prompt transports (chat platforms
via `_approval_notify_sync`, SSE/API via `_approval_notify`). A `/simplify-code`
pass surfaced a **third egress transport that was missed**: the TUI JSON-RPC
path. Three `register_gateway_notify` callbacks in `tui_gateway/server.py` emit
the raw `approval_data` — including the unredacted `command` Tirith flagged —
straight to the TUI client via `_emit("approval.request", ...)`:
- `tui_gateway/server.py:1043`, `:2557`, `:3919`

Verified still live on current `main` (`5937b9519`): the seam
`gateway.run._redact_approval_command` exists (from #50767) but the three TUI
lambdas don't use it.

## Fix

Route all three registrations through a new module-level
`_emit_approval_request(sid, data)` helper that redacts `payload["command"]`
via the shared `_redact_approval_command` seam before `_emit` — the same pattern
already applied to the other two transports. Single point, so the three call
sites can't drift.

## Tests

`tests/gateway/test_tui_approval_redaction.py`:
- `_emit_approval_request` emits a redacted command (real credential pattern),
  preserves non-command fields + command structure;
- handles missing/`None` command;
- a wiring guard asserting **no** registration emits the raw payload directly
  (exactly one raw `_emit("approval.request")` allowed — inside the helper).

Both behaviors mutation-checked (neutering the redaction fails the behavior
test; reverting a lambda to raw `_emit` fails the wiring guard).

## Attribution

The #48456 fix series originated from **@liuhao1024**'s #48462 (the original
report + chat-platform fix). This PR completes the remaining transport;
co-authored credit to @liuhao1024.

Relates to #48456 (third transport; #50767 closed the issue).