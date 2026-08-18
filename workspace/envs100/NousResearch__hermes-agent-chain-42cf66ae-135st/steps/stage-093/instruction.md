**fix: persist Google OAuth PKCE state for headless setup**

## Summary
- persist the pending Google OAuth state and code verifier between `--auth-url` and `--auth-code`
- keep using `google-auth-oauthlib`'s PKCE flow instead of bypassing PKCE with a manual token POST
- add regression tests for the headless/manual auth flow and document the temporary pending session file

## Why this approach
The bug in #1093 / #1101 is real, but the safer fix is to preserve and reuse the verifier/state across the two CLI invocations rather than disabling PKCE entirely. This keeps us on the library-supported flow and avoids owning a custom token exchange path.