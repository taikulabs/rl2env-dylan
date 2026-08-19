**fix(agent): add qwen and deepseek to TOOL_USE_ENFORCEMENT_MODELS**

Salvage of #28195 by @briandevans (squashed 2-commit stack: fix + test improvement). Supersedes already-.

**What:** Qwen3.x and DeepSeek-V3.x default to chatty/hallucinatory tool use without enforcement steering — agents narrate "calling tool X" without actually emitting a tool call, or run partial loops.

**How:** Add `qwen` and `deepseek` substrings to `TOOL_USE_ENFORCEMENT_MODELS` in `agent/prompt_builder.py`. Two new unit tests in `test_prompt_builder.py` and two integration tests in `test_run_agent.py` verify auto-mode injection for each model family.

Original PR: 
.