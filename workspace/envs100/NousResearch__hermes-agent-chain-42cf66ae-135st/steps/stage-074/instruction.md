**refactor: unify vision backend gating**

## Summary
- unify vision backend availability behind a single runtime resolver
- stop treating vision as effectively OpenRouter-only in setup and tools config
- make Codex, Nous, and custom OpenAI-compatible backends count consistently for vision tool availability