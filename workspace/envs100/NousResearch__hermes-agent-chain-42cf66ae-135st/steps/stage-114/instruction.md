**fix(gateway): make /status report live state and tokens**

## Summary
- make `/status` bypass the running-agent interrupt path so it can report live state during an active run
- persist actual per-run input/output token counts from the gateway agent result into the session store
- add focused regression coverage for both live `/status` and token persistence

## Root cause
- `/status` was checked after the generic interrupt gate, so if an agent was running the command got queued like normal user text and never produced a live status response
- session metadata updates only forwarded `last_prompt_tokens`, so `input_tokens`, `output_tokens`, and therefore `total_tokens` stayed at zero