**feat(gateway): notify users when session auto-resets**

## Summary

When a session expires (daily schedule or idle timeout) and is automatically reset, the user now receives a notification explaining what happened:

```
◐ Session automatically reset (daily schedule at 4:00). Conversation history cleared.
◐ Session automatically reset (inactive for 24h). Conversation history cleared.
```

### How it works

1. `_should_reset()` now returns a reason string (`"idle"` or `"daily"`) instead of bool
2. The reason is stored on `SessionEntry.auto_reset_reason`
3. When `_handle_message_with_agent()` detects `was_auto_reset`, it sends the notification via `adapter.send()` before processing the user's message
4. Excluded platforms (default: `api_server`, `webhook`) don't get notifications

### Config

```yaml
session_reset:
  mode: both
  at_hour: 4
  idle_minutes: 1440
  notify: true                              # default: true
  notify_exclude_platforms: [api_server, webhook]  # default
```

Set `notify: false` to disable globally. Add platform names to `notify_exclude_platforms` to suppress for specific platforms (ACP isn't a gateway Platform enum member so it's already excluded).

### Changes

- `gateway/session.py`: `_should_reset()` returns reason; `SessionEntry.auto_reset_reason` field
- `gateway/config.py`: `SessionResetPolicy.notify` + `notify_exclude_platforms` with `from_dict`/`to_dict` support
- `gateway/run.py`: notification sent before processing user message, with platform exclusion check
- 11 new tests

### Verification
- 5913 passed, no regressions

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_session_reset_notify.py`