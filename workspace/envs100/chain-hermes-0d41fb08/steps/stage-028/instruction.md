**feat(hindsight): feature parity, setup wizard, and config improvements**

## Summary

Ports missing features from the `hindsight-hermes` external integration package into the native plugin, enabling the external package to be dropped. **Only modifies files within the plugin boundary** — no core changes.

### Features
- **Tags**: `tags` on retain, `recall_tags` / `recall_tags_match` on recall
- **Recall config**: `recall_max_tokens`, `recall_max_input_chars`, `recall_types`, `recall_prompt_preamble`
- **Retain controls**: `retain_every_n_turns`, `auto_retain`, `auto_recall`, `retain_async` (via `aretain_batch`), `retain_context`
- **Bank config**: `bank_mission` and `bank_retain_mission` applied via Banks API during setup
- **Structured retain**: JSON format with per-message timestamps, full session accumulation with `document_id` for dedup
- **Setup wizard**: custom `post_setup()` with curses arrow-key picker, mode-aware dependency installation
- **New modes**: `local_external` (connect to existing instance), `openai_compatible` and `openrouter` LLM providers
- **Auto-upgrade**: detects outdated `hindsight-client` (<0.4.22) and upgrades automatically on session start
- **Debug logging**: comprehensive logs across all operations (visible with `hermes -vv`)

### Tests
46 unit tests covering config, tool handlers, prefetch, sync_turn, schemas, and availability.

### Docs
Updated plugin README and website memory-providers page.

### Not included
`retain_tool_calls` (including tool calls in retained content) requires a `turn_messages` parameter on the core `sync_turn()` ABC — filed separately for evaluation.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/plugins/memory/test_hindsight_provider.py`