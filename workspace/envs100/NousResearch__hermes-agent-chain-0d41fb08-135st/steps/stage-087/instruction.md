**fix(api): send tool progress as custom SSE event to prevent model corruption**

## Summary
Tool progress markers (`⏰ terminal`, `🔍 web_search`) were injected directly into `delta.content` chunks in the SSE stream. OpenAI-compatible frontends (Open WebUI, LobeChat, LibreChat) store `delta.content` verbatim as assistant messages and send them back — polluting conversation history and potentially causing models to imitate the markers instead of calling tools.

Sends tool progress as custom `event: hermes.tool.progress` SSE events instead. Per SSE spec, clients that don't understand custom events silently ignore them. Clients that do can render them as progress UI.

## Changes
- `gateway/platforms/api_server.py`: `_on_tool_progress` pushes tagged tuples, new `_emit()` helper routes to custom SSE event
- `tests/gateway/test_api_server.py`: Tests verify markers appear as custom events and do NOT leak into `delta.content`

## Test results
106 API server tests passing

Salvaged from #7014 (@Bartok9). .

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_api_server.py`