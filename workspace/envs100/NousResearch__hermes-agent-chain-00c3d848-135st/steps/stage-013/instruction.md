**fix: use output_text for assistant content in Codex Responses API**

## Summary

 — the Codex Responses API rejects `input_text` content type inside assistant messages. Only `output_text` and `refusal` are valid for assistant role.

## Root Cause

`_chat_content_to_responses_parts()` in `agent/codex_responses_adapter.py` hardcoded all text content to type `input_text` regardless of the message role. When an assistant message had list-format content (multimodal or structured), the resulting `input_text` parts were sent to the API, which rejected them:

```
Invalid value: 'input_text'. Supported values are: 'output_text' and 'refusal'.
param: 'input[109].content[0]'
```

## Fix

Added a `role` parameter to `_chat_content_to_responses_parts()` that selects the correct content type:
- User messages → `input_text`
- Assistant messages → `output_text`

Threaded this role through all three functions that handle content:
1. `_chat_content_to_responses_parts(content, role=role)` — emits correct type
2. `_chat_messages_to_responses_input()` — passes role, filters on correct type
3. `_preflight_codex_input_items()` — preserves correct type per role during validation

## Why it only triggers with list content

When assistant content is a plain string (the common case), it bypasses `_chat_content_to_responses_parts()` entirely and is emitted directly as a string. The bug only manifests when assistant content is a list of parts — which happens with multimodal messages or structured content.