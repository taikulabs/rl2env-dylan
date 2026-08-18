**fix(auth): use bearer auth for MiniMax Anthropic endpoints**

Salvage of #4002 by @kshitijk4poor onto current main.

## Summary

MiniMax's `/anthropic` endpoints implement Anthropic's Messages API but require `Authorization: Bearer` instead of Anthropic's native `x-api-key` header. Without this fix, MiniMax users get 401 errors in gateway sessions.

### Changes
- Adds `_requires_bearer_auth()` to detect MiniMax global (`api.minimax.io/anthropic`) and China (`api.minimaxi.com/anthropic`) endpoints
- Routes MiniMax through `auth_token` (Bearer) instead of `api_key` (x-api-key) in the Anthropic SDK
- Check runs before OAuth token detection so MiniMax keys aren't misclassified as setup tokens
- Native Anthropic auth behavior unchanged

### Salvage fixes
- Restored 3 existing test values corrupted by display-tool redaction artifacts in the original PR (`***` and `sk-ant...` replacing valid mock keys)