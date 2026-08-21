**fix(discord): properly route slash event handling in threads**

Discord slash commands in threads were missing `thread_id` in the `SessionSource`, routing to the parent channel session. `/usage` returned wrong data, `/reset` affected the wrong session.

Detects `discord.Thread` in `_build_slash_event` and sets `chat_type='thread'` with `thread_id`. Two tests added. 17 discord slash tests passing.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_discord_slash_commands.py`