**fix: prevent closed OpenAI client reuse across retries**

## Summary
- 
- preserve the shared client for direct-use paths, but recreate it defensively if Hermes detects it is already closed
- add current-main follow-up so `_streaming_api_call()` also uses request-local OpenAI clients during voice/TTS streaming
- add lifecycle regression coverage for retry-after-connection-error, closed shared-client recreation, concurrent isolation, and the streaming closed-client path

## Contributor credit
Salvages PR #1229 by cherry-picking the contributor commit onto current main with authorship preserved, plus a small current-main follow-up for `_streaming_api_call()`.
