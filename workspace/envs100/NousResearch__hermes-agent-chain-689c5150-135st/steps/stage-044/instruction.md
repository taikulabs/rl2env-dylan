**fix(cli): narrow Nous Hermes non-agentic warning to actual hermes-3/-4 models**

## What does this PR do?

The startup warning that Nous Research Hermes 3 & 4 models are not agentic fired on **any** model whose name contained the substring `hermes`, via a plain case-insensitive substring check. That false-positives on unrelated local Modelfiles such as `hermes-brain:qwen3-14b-ctx16k` — a tool-capable Qwen3 wrapper that happens to live under a custom `hermes` tag namespace — making the warning noise for legitimate setups.

This PR replaces the substring check with a narrow regex anchored on `^`, `/`, or `:` boundaries that only matches the real Hermes-3 / Hermes-4 chat family (e.g. `NousResearch/Hermes-3-Llama-3.1-70B`, `hermes-4-405b`, `openrouter/hermes3:70b`). Consolidates into a single helper `is_nous_hermes_non_agentic()` in `hermes_cli.model_switch` so the CLI and the canonical check don't drift, and routes the duplicate inline site in `cli.HermesCLI._print_warnings()` through the helper.