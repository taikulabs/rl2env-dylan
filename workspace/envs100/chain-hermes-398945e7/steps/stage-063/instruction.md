**feat(acp): add steer and queue slash commands**

## Summary
- advertise /steer and /queue in ACP available commands
- route /steer into the existing AIAgent.steer() mechanism when a turn is active
- queue /queue prompts and regular prompts submitted during an active ACP turn
- drain queued prompts after the current turn without racing session history

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/acp_adapter/test_acp_commands.py`