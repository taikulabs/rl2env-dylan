**fix(memory): keep inline memory-context mentions visible (salvage of #18383)**

## Salvage of #18383

Cherry-picks @BlackishGreen33's fix for the CLI output truncation when an
assistant response mentions the literal `<memory-context>` tag inline
(issue #18351). The PR branch was ~1858 commits behind `main`; cherry-picked
clean onto current `main` with attribution preserved.

## What's broken on `main`

`StreamingContextScrubber` enters span-strip mode at the first
`<memory-context>` substring it sees in streamed output and waits for a
closing tag. When the model just *mentions* the tag inline
(e.g. ``` In that previous `<memory-context>` block, ... ```), no close tag
follows and the rest of the answer is silently dropped.

Reproduced on current `origin/main`:

```python
from agent.memory_manager import StreamingContextScrubber
s = StreamingContextScrubber()
inp = "In that previous `<memory-context>` block, there was no info."
print(s.feed(inp) + s.flush())
# -> "In that previous `"          ← rest of the answer swallowed
```

## Fix

Only open a scrub span when the open tag sits at a **block boundary**:

1. `_is_block_boundary`: preceding text on the same line is whitespace-only
2. `_has_block_opener_suffix`: the char immediately after `<memory-context>`
   is `\r` or `\n`

A pending one-tag suffix is held across deltas so a chunk ending exactly at
`<memory-context>` waits for the next char to decide block-vs-inline.

This matches the sole producer `build_memory_context_block()` in
`agent/memory_manager.py`, which always emits:

```
<memory-context>\n
[System note: ...]\n
\n
{clean}\n
</memory-context>
```

— always at line start, always followed by `\n`. Single producer, single
consumer (`agent/agent_init.py` → `run_agent.py`); no other `<memory-context>`
emitter exists in the tree.