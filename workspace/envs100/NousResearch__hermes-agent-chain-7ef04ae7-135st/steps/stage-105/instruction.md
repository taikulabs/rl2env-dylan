**fix(streaming): handle adapters that return final responses (salvage #11780)**

## Summary
ACP Copilot no longer crashes on the first message — adapters that accept `stream=True` but return a completed response object instead of a chunk iterator now fall back to non-streaming cleanly.

Root cause: `copilot-acp` ignores `stream=True` and returns a final response object. The streaming loop then hit `for chunk in stream` on a non-iterable `SimpleNamespace`, raising `'types.SimpleNamespace' object is not iterable`. .

## Changes
- `agent/chat_completion_helpers.py`: after `chat.completions.create(**stream_kwargs)`, detect a populated `choices` list (a final-response object). Log it, set `_disable_streaming` for the session, fire the content + reasoning deltas so output still reaches the user, and return the object instead of iterating it.
- `tests/run_agent/test_streaming.py`: focused test that a final-response object disables streaming and returns the response with deltas fired.

Salvaged from @LeonSGP43's #11780. The streaming loop was extracted out of `run_agent.py` into `agent/chat_completion_helpers.py` since the PR was authored, so the guard was ported to its new home (`self.` → `agent.`, local `_fire_first_delta()` helper). Logic and test are unchanged.

## Validation
| | Before | After |
|---|---|---|
| copilot-acp first message | `'SimpleNamespace' object is not iterable` | falls back to non-streaming, replies |
| content delta | — | fired via `stream_delta_callback` |
| reasoning delta | — | fired via `reasoning_callback` |
| streaming tests | — | 42/42 green |

E2E verified the real `interruptible_streaming_api_call` path returns the object, sets `_disable_streaming`, and fires both content and reasoning deltas.

## Infographic
![Streaming fallback guard](https://v3b.fal.media/files/b/0aa06db6/hVAxRgorWn-MENl52bWUt_Q6v4Mliz.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/run_agent/test_streaming.py`