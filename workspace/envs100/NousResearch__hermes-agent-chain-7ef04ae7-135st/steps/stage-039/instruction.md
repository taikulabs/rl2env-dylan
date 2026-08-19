**fix(agent): stream copilot ACP chat completions**

## Summary
Copilot ACP now works on the streaming chat-completions path instead of crashing on the first chunk. The ACP shim returns OpenAI-style iterable stream chunks when `stream=true`, and parses tool calls into real `ChatCompletionMessageToolCall` SDK objects so downstream handling matches every other provider.

Root cause: `copilot-acp` resolves to `api_mode="chat_completions"`, the streaming path. `interruptible_streaming_api_call` does `for chunk in stream`, but the shim ignored `stream` and returned a one-shot `SimpleNamespace` → `TypeError: 'SimpleNamespace' object is not iterable`.

## Changes
- `agent/copilot_acp_client.py`: `_create_chat_completion` accepts `stream` and, when set, returns iterable chunks via `_completion_to_stream_chunks` — a **data chunk** (content + tool-call deltas with indices + `finish_reason`) followed by a separate **usage chunk** with empty `choices`. Parsed ACP tool calls are built as `ChatCompletionMessageToolCall(id, call_id, function=Function(...))`, preserving Hermes `call_id` metadata.
- `tests/agent/test_copilot_acp_client.py`: regression coverage for stream text chunks, stream tool-call deltas, OpenAI SDK tool-call shape, and timeout-object coercion on streaming requests.

The two-chunk split matters: the consumer reads `chunk.usage` **only** when `chunk.choices` is empty, so a single combined chunk would silently drop usage accounting.

## Validation
| Path | Result |
|---|---|
| `tests/agent/test_copilot_acp_client.py` | 11 passed |
| copilot-acp stays on chat_completions / uses ACP client | 2 passed |
| E2E vs real `interruptible_streaming_api_call` consumer loop | text + tool-call + usage capture verified |
| Non-stream path | unchanged (still returns one-shot completion) |

Salvage of @sgaofen's PR #14438, 

## Infographic
![infographic](https://v3b.fal.media/files/b/0aa033ab/lP06fuozzdnMeSvOsdnAw_PkjDtOdd.png)