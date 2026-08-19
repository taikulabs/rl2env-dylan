**fix: prevent duplicate update prompt spam in gateway watcher**

## Summary

The `_watch_update_progress()` poll loop never deleted `.update_prompt.json` after forwarding the prompt to the user, causing the same "Would you like to configure new options now?" prompt to be re-sent every 2-second poll cycle — flooding the chat with duplicate messages.

**Two fixes:**
1. Delete `.update_prompt.json` after forwarding — the update process only polls for `.update_response`, not the prompt file
2. Guard re-sends with `_update_prompt_pending` check — prevents duplicates even under race conditions

**Test:** Added regression test asserting the prompt is sent exactly once across multiple poll cycles.