**fix(gateway): route synthetic background events to their originating session**

## Summary
- route queued watch notifications via the originating session instead of the currently active foreground event
- attach `session_key` plus routing metadata to queued watch events in `tools/process_registry.py`
- resolve synthetic watch/completion event sources via `session_key -> session_store.origin`, with safe fallback parsing
- preserve the correct `chat_type` for synthetic completion events so threaded group traffic does not get rebuilt as bogus DM sessions

This addresses the cross-topic/session bleed described in #9532 and the related synthetic-session reconstruction bug behind the screenshot symptom.