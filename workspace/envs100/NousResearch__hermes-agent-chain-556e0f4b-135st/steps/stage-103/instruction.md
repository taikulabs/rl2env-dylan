**fix(gateway): prevent stale memory overwrites by flush agent**

## Summary

. Salvages ideas from #2675 (devorun) and #2676 (dlkakbs).

The gateway memory flush agent spawns a temporary AIAgent on session reset/expiry to review old conversation history and save memories. It had no awareness of memory changes made after that conversation ended — by the live agent, cron jobs, or concurrent sessions — causing silent overwrites of newer entries.

### Root cause

The flush agent received the old conversation + a generic "save important facts" prompt. While current memory was technically present in its system prompt, there was no explicit connection between "here's what's already saved" and "review this conversation." The model would focus on the old conversation and `replace` entries with stale versions, reverting changes that happened after the conversation ended.

### The fix (two parts)

**1. Cron session bypass** (from #2675)
Skip memory flush entirely for cron sessions (`cron_*` session IDs). Cron sessions are headless with no meaningful user conversation to extract memories from.

**2. Live memory injection into flush prompt**
Read the current MEMORY.md and USER.md from disk and inject them directly into the flush prompt (user turn). The flush agent now sees the current memory state right next to its instructions, so it can:
- See what's already captured and skip duplicates
- Make informed `replace` decisions only when the conversation genuinely supersedes existing entries
- Avoid blindly overwriting entries added by other sessions or cron jobs

This is better than the add-only constraint because the model retains full tool access and can make intelligent decisions with complete information.

### Why not the other approaches?

- **Add-only constraint**: Soft — relies on the LLM following instructions. Also prevents legitimate `replace` operations when information genuinely changed.
- **Config opt-out**: Implementation read config.yaml inline with raw YAML parsing instead of using the gateway's existing config system.
- **Disabling flush entirely**: Loses the value of automatic memory curation on session reset.

## Changes

- `gateway/run.py`: Added cron session bypass + live memory content injection in `_flush_memories_for_session()`
- `tests/gateway/test_flush_memory_stale_guard.py`: 7 tests covering cron bypass, memory injection, empty/missing files, and prompt structure