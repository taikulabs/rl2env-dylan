**fix(gateway): remove user-facing compression warnings**

Auto-compression still runs silently with server-side logging, but no longer sends messages into the user's chat.

Removed all four user-facing compression notifications:
- "Session is large... Auto-compressing" (pre-compression)
- "Compressed: N → M messages" (post-compression)  
- "Session is still very large after compression" (post-compression warning)
- "Auto-compression failed" (error warning)
- Rate-limit tracking dict + cooldown (only existed for these warnings)

The /compact command response is unchanged — that's user-initiated.