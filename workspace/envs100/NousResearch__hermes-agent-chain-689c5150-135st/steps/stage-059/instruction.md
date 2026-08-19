**fix: honor interrupts during MCP tool waits**

## What does this PR do?
Makes MCP tool calls interruptible so a user message can break out of a blocked main agent turn instead of waiting for the MCP call to finish.

## Related Issue
Support-driven fix for the new process monitoring workflow becoming effectively uninterruptible when the agent is waiting on an MCP terminal/process call.