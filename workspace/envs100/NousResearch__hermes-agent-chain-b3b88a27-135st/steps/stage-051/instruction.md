**fix(surrogates): sanitize reasoning_content / reasoning_details so surrogate UnicodeEncodeError actually recovers**

## Summary
Surrogate recovery now actually recovers on models that emit lone surrogates in reasoning output. Previously, `_sanitize_messages_surrogates()` only walked `content`/`name`/`tool_calls` — so a surrogate in `reasoning` / `reasoning_content` / `reasoning_details` sailed through the proactive pass, crashed `json.dumps()` in the OpenAI SDK, and the recovery block's `_surrogates_found` returned False. No retry fired, three attempts burned, user saw "API call failed after 3 retries: 'utf-8' codec can't encode characters in position N-M: surrogates not allowed".

Root cause: `_sanitize_messages_non_ascii()` was extended in #10537 to walk extra string fields, but the surrogate counterpart was never updated. Byte-level reasoning models (xiaomi/mimo-v2-pro, kimi, glm) trigger this regularly.

Reported by a user on Discord hitting it with `xiaomi/mimo-v2-pro` via Nous.

## Changes
- **run_agent.py**
  - `_sanitize_messages_surrogates`: walk any extra string fields (reasoning, reasoning_content, etc.) and recurse into nested dict/list values (reasoning_details[].summary/text, encrypted_content, etc.).
  - `_sanitize_structure_surrogates`: new recursive walker, mirror of `_sanitize_structure_non_ascii` for surrogate recovery.
  - UnicodeEncodeError recovery block: also sanitize `api_messages`, `api_kwargs`, and `prefill_messages` — not just the canonical `messages` list. The API-copy is what actually gets serialized, and it carries `reasoning_content` transformed from `reasoning` at build time. Always retry on detected surrogate errors, not only when something was stripped (skill lesson from #10537: gate on error type, not on found-anything).
- **tests/cli/test_surrogate_sanitization.py**
  - New classes: `TestReasoningFieldSurrogates` (reasoning/reasoning_content/reasoning_details flat + deeply nested), `TestSanitizeStructureSurrogates` (structure walker coverage), `TestApiMessagesSurrogateRecovery` (integration case reproducing the exact api_messages shape that was crashing).

## Validation
| | Before | After |
|---|---|---|
| Surrogate in `reasoning_content` | `json.dumps` crashes, 3 retries fail silently | Stripped, request succeeds |
| Surrogate in nested `reasoning_details[].summary` | Same failure | Caught by recursive walker |
| Recovery block retry decision | `_surrogates_found = False` → fall through | Always retry on surrogate UnicodeEncodeError within budget |
| `tests/cli/test_surrogate_sanitization.py` | 15 passed | 28 passed |
| `tests/run_agent/` | 760 passed | 760 passed |

E2E reproduction (run locally): built api_messages with surrogates in reasoning_content + reasoning_details, confirmed `json.dumps(..., ensure_ascii=False).encode('utf-8')` (the SDK's exact code path) now succeeds with zero surrogate leaks.

## Related
- Follows the same design as #10537 which extended the non-ASCII sanitizer; this mirrors that pattern for the surrogate path.
- Skill: `unicode-encode-error-http-diagnosis` (the "gate on error type, not on found-anything" rule).