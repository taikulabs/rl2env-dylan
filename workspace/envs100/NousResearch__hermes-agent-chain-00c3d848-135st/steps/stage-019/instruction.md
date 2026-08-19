**fix(agent): preserve Codex message items for replay**

## What does this PR do?

Preserves Codex Responses API assistant message items (`id`, `phase`, and `status`) across session persistence and replay.

This is intended to fix avoidable prompt-cache misses in Codex sessions. Previously, follow-up turns flattened prior assistant output messages to plain text, dropping the structured Responses API metadata that Codex uses for prompt-prefix continuity. For newer Codex models, OpenAI documents that assistant message `phase` should be preserved and resent on follow-up requests; keeping the full message item shape improves cache affinity and avoids degrading prefix-cache performance. Preserving `status` also prevents incomplete or in-progress assistant messages from being replayed as completed.

The change stores `codex_message_items` alongside existing `codex_reasoning_items`, replays those structured message items back into Responses API input, strips the Codex-only field from strict chat-completions providers, and updates incomplete-response duplicate detection so newer Codex message item state is not silently dropped.

It also fixes a transport registry ordering bug discovered while running the changed-test set: importing one transport directly could partially populate the registry and make other valid API modes unavailable. The registry now performs discovery on misses, not only when empty.

## Related Issue

N/A