**fix: preserve dots in model names for OpenCode Zen and ZAI providers**

## Summary

Fixes the HTTP 400 when using OpenCode Zen with dotted model names like `minimax-m2.5-free`, `gpt-5.4`, `glm-5.1`. The dot-to-hyphen conversion was applied to ALL models on Zen, but only Claude models need it.

Also fixes the same issue for ZAI provider (`glm-5.1` was being mangled to `glm-5-1`).

### Two-layer fix

**Layer 1 (`model_normalize.py`):** Remove `opencode-zen` from blanket `_DOT_TO_HYPHEN_PROVIDERS`. Add explicit mixed-mode block: Claude stays hyphenated (Zen's Claude endpoint uses anthropic_messages which expects `claude-sonnet-4-6`), all other models preserve dots.

**Layer 2 (`run_agent.py _anthropic_preserve_dots`):** Add `opencode-zen` and `zai` to provider allowlist. Broaden URL check from `opencode.ai/zen/go` to `opencode.ai/zen/` to cover both Go and Zen endpoints. Add `bigmodel.cn` for ZAI URL detection.

Also adds `glm-5.1` to ZAI model lists in `models.py` and `setup.py`.