**fix: clamp 'minimal' reasoning effort to 'low' on Responses API**

## Summary

GPT-5.4's Responses API supports `none`/`low`/`medium`/`high`/`xhigh` but **not** `minimal`. Users who configure `minimal` reasoning effort (valid on OpenRouter and GPT-5) would get a 400 error when routed through the native OpenAI Codex Responses path.

Clamps `minimal` → `low` in the `codex_responses` `_build_api_kwargs` path before sending.

Inspired by OpenClaw v2026.4.14-beta.1 which fixed the same gap.

## Changes
- **run_agent.py**: 6-line effort clamp dict after reasoning effort resolution
- **tests/run_agent/test_run_agent_codex_responses.py**: 2 new tests — clamp verification + passthrough for supported levels