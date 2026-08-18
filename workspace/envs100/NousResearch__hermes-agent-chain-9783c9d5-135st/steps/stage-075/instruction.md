**fix(browser): guard LLM response content against None in snapshot and vision**

Salvage of PR #3532 (binhnt92). .

Reasoning-only models (DeepSeek-R1, QwQ via OpenRouter) return `content=None`, causing null snapshots and null vision analysis. Guards both sites with `(content or "").strip()` and sensible fallbacks.

7 tests, 54 browser tests total passing.

Co-Authored-By: binhnt92 <binhnt92@users.noreply.github.com>