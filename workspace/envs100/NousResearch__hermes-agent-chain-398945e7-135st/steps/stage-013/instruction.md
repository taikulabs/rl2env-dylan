**fix(tui): responsive /compress with live progress + CLI-parity feedback**

## Summary
- Route `session.compress` through the TUI gateway long-handler pool so manual compaction never blocks the JSON-RPC loop.
- Show a single live progress line in the transcript with a braille spinner glyph and live message + token estimate, instead of a silent wait.
- Return a structured summary (`headline`, `token_line`, optional `note`) shared with the classic CLI's `/compress` flow, so the final result reads like the CLI.
- Mirror the gateway's `status.update(kind: "compressing")` event into the transcript so the live line stays visible while the LLM call is in flight.

## Background
Profiled the compaction path locally on a long TUI session:

- Synthetic 1,000-message, ~345k-token compressor run with the LLM summary stubbed: ~0.002s.
- Cold TUI wrapper run: ~0.745s, mostly lazy imports/tool discovery.
- Pre-fix dispatch check: `session.compress` ran inline on the gateway loop, so other RPCs blocked behind it for the full LLM compaction wall time.
- Post-fix dispatch check: `session.compress` returns immediately (~0.1ms), and a concurrent `fast.ping` also returns in ~0.1ms.

## What you see in the TUI now
```
· /compress
⠋ compressing 242 messages (~77,331 tok)…
···
· ✓ Compressed: 242 → 10 messages
·   Rough transcript estimate: ~77,331 → ~4,257 tokens
```