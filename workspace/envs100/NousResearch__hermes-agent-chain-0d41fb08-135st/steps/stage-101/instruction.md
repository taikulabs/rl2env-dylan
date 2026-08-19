**fix: honor session-scoped gateway model overrides**

## Summary

Honor session-scoped `/model` overrides for fresh gateway-created agents.

This fixes a routing bug where a gateway session could be switched to `gpt-5.4` on `openai-codex`, but helper or rebuilt agents for that same session would still re-resolve provider/runtime from global config and silently fall back to a different provider such as `nous`.

That mismatch could cause requests to hit a paid provider instead of the intended subscription-included route.

## What changed

- add a session-aware gateway resolver that prefers `_session_model_overrides` when a complete override exists
- use that resolver for fresh agent construction in:
  - main gateway agent rebuild path
  - `/background`
  - `/btw`
  - manual `/compress`
  - auto-compress hygiene agent
  - pre-reset / pre-resume memory flush helper
- thread `session_key` through memory flush so it can honor the correct session override
- add regression tests covering:
  - main `_run_agent` path
  - background-task helper path
- update the existing resume test to reflect the new flush helper signature

## User-visible impact

Before this fix:

- a chat could appear to be using `gpt-5.4` on `openai-codex`
- but helper/rebuilt agents for that chat could route to the default provider instead
- if that provider was billable, users could see unexpected spend

After this fix:

- fresh gateway-created agents for a session consistently honor the session's active model/provider/runtime override