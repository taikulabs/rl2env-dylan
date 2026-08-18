**fix(prompt-caching): skip top-level cache_control on role:tool for OpenRouter**

Salvage of PR #2373 by @teyrebaz33. .

OpenRouter hangs silently when `cache_control` appears top-level on `role:tool` messages. The native Anthropic adapter moves it inside the `tool_result` block, but OpenRouter's chat_completions path never does — so the invalid field causes a silent hang with no error.

Fix: `_apply_cache_marker()` and `apply_anthropic_cache_control()` now take a `native_anthropic` flag. When False (OpenRouter), tool messages are skipped. When True (native Anthropic Messages API), existing behavior is preserved.

4 files, +17/-8. 91 caching + adapter tests pass. Authorship preserved.