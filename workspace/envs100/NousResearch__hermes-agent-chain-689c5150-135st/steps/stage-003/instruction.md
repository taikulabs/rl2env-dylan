**feat(gateway): surface natural mid-turn assistant messages in chat platforms**

## Summary

Surfaces completed assistant commentary between tool calls as separate chat messages on messaging platforms. When a model says "I'll inspect the repo first." before calling tools, users now see that message in Telegram/Discord/etc. instead of silence for minutes.

**Enabled by default** — `display.interim_assistant_messages: true`. Can be disabled per-user.

## Changes

- `run_agent.py`: New `interim_assistant_callback` on AIAgent, fired at 3 points where interim assistant messages are appended to conversation (tool-calling loop, codex responses, incomplete continuations). Strips think blocks, tracks already-streamed text to avoid double delivery.
- `gateway/run.py`: Wires callback, routes through GatewayStreamConsumer when available, falls back to direct send. Disabled for webhooks. Handles `response_previewed` to prevent double-delivery when interim message matches final response.
- `gateway/stream_consumer.py`: New `on_commentary()` / `_send_commentary()` methods. New `final_response_sent` property. Refactors `_reset_segment_state()` and `_send_or_edit()` — includes bug fix for cursor not stripped from fallback prefix (affected no-edit platforms like Signal).
- `hermes_cli/config.py`: New `display.interim_assistant_messages` config key, config migration v14→v15.
- Docs and example config updated.
- Tests: 11 new tests covering default-on, explicit-off, tool_progress/streaming independence, queued messages, previewed final response, stream consumer commentary, no-message-id fallback.

## vs PR #5017

PR #5017 adds a new `send_user_message` tool — schema bloat, requires model to learn new behavior. This PR surfaces what models already emit naturally. Zero tool footprint, zero model behavior change.