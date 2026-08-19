**fix: notify active sessions on gateway shutdown + update health check**

## Summary

Addresses three gateway lifecycle stability issues from user reports of agents being killed mid-work with no notification.

### Changes

**1. Notify active sessions before shutdown (new)**
When the gateway receives SIGTERM or `/restart`, `_notify_active_sessions_of_shutdown()` sends a message to every chat with an active agent BEFORE the drain starts (while adapters are still connected):
- Shutdown: `⚠️ Gateway shutting down — Your current task will be interrupted.`
- Restart: `⚠️ Gateway restarting — Your current task will be interrupted. Use /retry after restart to continue.`

Deduplicates per-chat (multiple users in a group get one notification). Best-effort — send failures are logged and swallowed so they never block shutdown.

**2. Skip .clean_shutdown marker when drain timed out**
Previously, graceful SIGTERM always wrote `.clean_shutdown`, even when agents were force-interrupted after the drain timeout. The next startup would skip session suspension, leaving interrupted sessions in a broken state (trailing tool response, no final assistant message → stuck session on resume). Now the marker is only written if the drain completed cleanly. Interrupted sessions get properly suspended on next startup.

This also helps with #7536 (stuck session resume loops) — sessions interrupted during shutdown will now be auto-suspended instead of resuming into a broken state.

**3. Post-restart health check for `hermes update`**
`cmd_update()` now verifies the gateway service actually survived after `systemctl restart`:
- Sleep 3s → `systemctl is-active` check
- If dead: retry once (transient startup failures often resolve)
- If still dead: print actionable diagnostics (journalctl command + manual restart hint)

Previously, `systemctl restart` returning 0 was taken as success even if the service crashed immediately — leaving the gateway silently dead for days.

**Also ** — already fixed on main (`/restart` handler correctly detects systemd via `INVOCATION_ID` and uses `via_service=True`).

## Related issues
- 
- 
- Partially addresses #4493, #7536, #5646 (Phase 2 follow-up planned)