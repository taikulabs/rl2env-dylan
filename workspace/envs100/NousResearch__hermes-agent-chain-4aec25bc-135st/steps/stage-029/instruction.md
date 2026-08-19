**fix(compressor): strip historical media after compression (salvage of #19951)**

## Summary
Salvage of #19951 — conversations that include large pasted images survive context compression instead of wedging a few turns later.

Port from Kilo-Org/.

## Root cause
`ContextCompressor.compress()` summarises the middle of the conversation but leaves head + tail messages untouched. When a user pastes a multi-MB screenshot in the protected tail, every subsequent turn keeps re-shipping that base64 blob, eventually breaching the provider's request-size limit even though compression looked successful.

## Changes
- `agent/context_compressor.py` (+~120): new `_strip_historical_media(messages)` + helpers (`_is_image_part`, `_content_has_images`, `_strip_images_from_content`). Finds the newest user message with an image part and replaces image parts in all earlier messages with `{"type": "text", "text": "[Attached image — stripped after compression]"}`. Called from `compress()` right after `_sanitize_tool_pairs`. Handles OpenAI chat (`image_url`), Responses API (`input_image`), and Anthropic native (`image`) shapes. Shallow copies only; inputs never mutated.
- `tests/agent/test_compressor_historical_media.py` (+262): 27 tests — helper unit tests, strip-logic edge cases (no images, only-first-message image, non-dict entries, idempotence, non-mutation), and an integration test through the real `compress()` path.

## Port notes
Kilo's version gates on "has a completed summary message"; the hermes-agent equivalent is "compress() ran at least once," which is automatically true when the helper is called from inside `compress()` — so the gate is implicit rather than a separate boolean. Anchors on "newest user with images" rather than Kilo's "newest non-synthetic user part" because hermes-agent's synthetic-user messages (todo snapshots, etc.) are text-only and can't accidentally become the anchor.

## Validation
| | Result |
|---|---|
| `tests/agent/test_compressor_historical_media.py` + `test_context_compressor.py` | 107/107 |
| E2E (two-image conversation) | Newest image preserved, older replaced with placeholder, input not mutated |

## Existing behaviour preserved
- `_try_shrink_image_parts_in_messages` (post-hoc rescue on "image too large") still runs unchanged.
- `_prune_old_tool_results` is unchanged.
- `_preprocess_anthropic_content` / `_prepare_messages_for_non_vision_model` (non-vision stripping) are unchanged.
- Conversations that never trigger compression are unaffected.

## Source
Kilo-Org/. Originally scouted in #19951.