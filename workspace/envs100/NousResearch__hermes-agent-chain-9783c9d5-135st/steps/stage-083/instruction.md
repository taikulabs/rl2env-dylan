**fix(email): close SMTP and IMAP connections on failure**

Salvage of #1753 by @Himess onto current main.

## Summary

Fixes connection leaks in the email gateway adapter:

- **SMTP** (`_send_email`, `_send_email_with_attachment`): Wrapped `starttls()`/`login()`/`send_message()` in try/finally. `quit()` in finally block, with `close()` fallback if quit also fails.
- **IMAP** (`_fetch_new_messages`): Nested try/finally after `IMAP4_SSL()` so `logout()` runs unconditionally — including on early returns and mid-loop exceptions.

## Tests

4 new tests verifying cleanup on failure:
- SMTP quit called on send_message failure
- SMTP close called when quit also fails  
- IMAP logout called on uid fetch failure
- IMAP logout called on early return (no unseen)

All 69 email tests pass.

---
Original PR: #1753 by @Himess — cherry-picked with authorship preserved.