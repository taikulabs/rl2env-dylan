**fix(gateway): remove user-facing compression warnings**

Auto-compression still runs silently with server-side logging, but no longer sends messages into the user's chat.

Removed all four user-facing compression notifications:
- "Session is large... Auto-compressing" (pre-compression)
- "Compressed: N → M messages" (post-compression)  
- "Session is still very large after compression" (post-compression warning)
- "Auto-compression failed" (error warning)
- Rate-limit tracking dict + cooldown (only existed for these warnings)

The /compact command response is unchanged — that's user-initiated.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_session_hygiene.py`