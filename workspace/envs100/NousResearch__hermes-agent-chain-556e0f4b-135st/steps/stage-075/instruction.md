**fix(provider): prevent Anthropic fallback from inheriting non-Anthropic base_url + fix(update): reset on stash conflict**

## Summary

Two cherry-picked fixes from #2385 by @dieutx, split into separate commits.

### Commit 1: Anthropic base_url leak ()
When primary provider is `openai-codex` with `base_url: chatgpt.com/backend-api/codex` and fallback is `anthropic`, the Codex base URL leaked into the Anthropic client — Claude requests went to ChatGPT's endpoint and got 403 HTML back.

Fix: only honor `config.model.base_url` for Anthropic when `config.model.provider == "anthropic"`. Two files: `runtime_provider.py` and `auxiliary_client.py`.

### Commit 2: Stash restore conflict detection
`_restore_stashed_changes()` now detects unmerged files after `git stash apply` (even when returncode is 0) and does `reset --hard` to clean up. Prevents leaving the working tree in a broken state with conflict markers.

All 5686 tests pass.