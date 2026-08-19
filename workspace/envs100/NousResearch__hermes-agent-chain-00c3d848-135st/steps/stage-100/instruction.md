**fix(cron): preserve Telegram topic delivery targets**

## What does this PR do?

Fixes cron delivery for explicit Telegram forum topic targets such as `deliver: telegram:GROUP_ID:THREAD_ID`.

Cron delivery parsed the original `THREAD_ID` correctly, but then resolved the bare `GROUP_ID` through the channel directory. When the directory returned just the bare group id, `_resolve_single_delivery_target()` replaced both `chat_id` and `thread_id`, dropping the already-parsed topic id. Telegram then received no `message_thread_id` and delivered to the default topic.

This changes the merge so a resolved channel id updates `chat_id`, but only replaces `thread_id` when the resolved value actually includes a thread/topic id.

## Related Issue

Reported from Discord support: cron jobs using `deliver: telegram:GROUP_ID:THREAD_ID` landed in the group default topic when the bare group id existed in the channel directory.