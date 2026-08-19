**fix(discord): properly route slash event handling in threads**



Discord slash commands in threads were missing `thread_id` in the `SessionSource`, routing to the parent channel session. `/usage` returned wrong data, `/reset` affected the wrong session.

Detects `discord.Thread` in `_build_slash_event` and sets `chat_type='thread'` with `thread_id`. Two tests added. 17 discord slash tests passing.
