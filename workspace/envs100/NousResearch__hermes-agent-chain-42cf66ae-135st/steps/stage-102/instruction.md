**fix(gateway): isolate DM sessions by chat_id**

## Summary
- isolate all DM gateway sessions by chat_id instead of collapsing non-WhatsApp DMs into a shared agent:main:<platform>:dm key
- preserve thread_id differentiation within a DM chat and keep best-effort fallbacks when chat_id is missing
- update gateway tests to cover the new DM session-key behavior and interrupt-key expectations