**fix(run_agent): recover primary client on openai transport errors**

## Summary

Salvage of #6795 by @helix4u (cherry-picked onto current main).

Adds `APIConnectionError` and `APITimeoutError` to `_TRANSIENT_TRANSPORT_ERRORS` so the primary client rebuild path fires for OpenAI SDK transport errors — the most common error types from local LLM endpoints (LM Studio, Ollama, llama.cpp, vLLM).

**The gap:** The error classifier already classified these as transient transport errors (retries work), but when retries exhausted, `_try_recover_primary_transport()` only checked for raw httpx types (`ReadTimeout`, `ConnectTimeout`, etc.). The OpenAI SDK wraps httpx errors into `APIConnectionError`/`APITimeoutError` before they reach our code, so the recovery path never triggered. Sessions would get stuck until `/new`.

Complements #6967 (stream read timeout increase): that PR reduces how often timeouts occur, this PR fixes what happens when they do.

## Changes
- +2 entries in `_TRANSIENT_TRANSPORT_ERRORS` frozenset (run_agent.py)
- +2 regression tests (test_primary_runtime_restore.py)