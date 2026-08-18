**feat(honcho): add opt-in initOnSessionStart for tools mode and respect explicit peerName**

### **Summary**
This PR makes Honcho tools mode initialization configurable and fixes a peer naming edge case in gateway environments.

- Adds an opt-in config flag: initOnSessionStart (default false)
- In recallMode="tools", when enabled, initializes Honcho session during initialize() (eager init)
- Preserves tools-mode semantics: no automatic context injection
- Fixes gateway user_id overriding explicit peerName; now user_id is only a fallback when peerName is not set

### **Problem**
In tools mode, Honcho session init is lazy (first honcho_* tool call).  
Before that first tool call, sync_turn() can no-op due to missing manager/session state, so early conversation turns are not persisted to Honcho.

Also, in gateway flows, explicit peerName could be unintentionally overwritten by gateway user_id (e.g. Telegram chat id), which is not expected when peerName is explicitly configured.

### **Solution**

**Commit 1**: initOnSessionStart (opt-in eager init in tools mode)
- Add init_on_session_start: bool = False to HonchoClientConfig
- Resolve from config using existing precedence: host block > root > default false
- In initialize(), when recallMode="tools" and initOnSessionStart=true, call _do_session_init() immediately
- Keep prefetch() behavior unchanged in tools mode (still returns empty)

**Commit 2:** peerName override fix
- Change gateway override logic from:
  if _gw_user_id:
to:
  if _gw_user_id and not cfg.peer_name:
- Explicit peerName is respected
- user_id remains fallback for multi-user scoping when peerName is absent

**Why this is non-breaking**
1) Default behavior is unchanged (initOnSessionStart defaults to false)  
2) tools-mode no-injection semantics are unchanged (prefetch() remains empty in tools mode)  
3) Multi-user gateway behavior is preserved when peerName is not set  
4) No new dependency; implementation follows existing config/session patterns

Config examples

```json
{
  "recallMode": "tools",
  "initOnSessionStart": true,
  "peerName": "Alice"
}

{
  "hosts": {
    "hermes": {
      "recallMode": "tools",
      "initOnSessionStart": true
    }
  }
}

```
**Files changed**
- plugins/memory/honcho/__init__.py
- `plugins/memory/honcho/client.py`
- tests/honcho_plugin/test_client.py
- tests/honcho_plugin/test_session.py

**Test matrix**
- initOnSessionStart default false when absent
- root-level initOnSessionStart=true parsed correctly
- host-level value overrides root-level value
- tools + initOnSessionStart=false keeps lazy init behavior
- tools + initOnSessionStart=true performs eager init
- prefetch() remains empty in tools mode for both lazy/eager paths
- explicit peerName is not overridden by gateway user_id
- user_id is used when peerName is absent

Validation
- Local suite: tests/honcho_plugin/ -> 134 passed
- Manual E2E validation: Telegram gateway and CLI flows verified
- No regressions observed in honcho plugin tests

### Notes
- This PR intentionally keeps scope narrow (no unrelated changes).
- Behavior change is opt-in only.