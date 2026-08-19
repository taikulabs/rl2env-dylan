**feat: /compress <focus> — guided compression with focus topic**

## Summary

Adds an optional focus topic to `/compress`: typing `/compress database schema` guides the summariser to preserve information related to the focus topic (60-70% of summary budget) while compressing everything else more aggressively.

Works identically on **both CLI and all gateway platforms** (Telegram, Discord, etc.).

### Usage

```
/compress                     # standard compression (unchanged behavior)
/compress database schema     # preserve DB schema details, compress rest aggressively
/compress authentication flow # preserve auth details, compress rest aggressively
```

## Implementation

- **context_compressor.py**: `focus_topic` parameter on `_generate_summary()` and `compress()`; appends a FOCUS TOPIC guidance block to the LLM summarisation prompt
- **run_agent.py**: `focus_topic` parameter on `_compress_context()`, passed through to the compressor
- **cli.py**: `_manual_compress()` extracts focus topic from command string; preserves existing `manual_compression_feedback` integration (no regression from #7459)
- **gateway/run.py**: `_handle_compress_command()` extracts focus from event args — full gateway parity
- **commands.py**: `args_hint="[focus topic]"` on /compress CommandDef

## What's NOT changed
- No changes to prompt caching
- No changes to message flow invariants
- `/compress` without arguments works exactly as before
- All existing compression feedback (`manual_compression_feedback` module) preserved

## Test results
```
197 passed — all compression, CLI, commands, and gateway tests
```

15 new tests across:
- `tests/cli/test_compress_focus.py` — CLI focus extraction and passthrough
- `tests/agent/test_compress_focus.py` — compressor prompt injection
- `tests/gateway/test_compress_focus.py` — gateway focus extraction and passthrough

Salvaged from PR #7459. Inspired by Claude Code's `/compact <focus>`.