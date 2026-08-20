**fix: email adapter IMAP UID tracking and SMTP TLS verification**

## Summary
- salvage PR #994 onto current main by switching the email gateway adapter from IMAP sequence numbers to stable UIDs and by verifying SMTP STARTTLS certificates in all adapter send paths
- preserve the contributor’s test updates so email adapter coverage matches the UID-based behavior
- add a small follow-up hardening fix on top: the standalone `send_message_tool` email path now also passes an explicit default SSL context to `starttls()`, with regression coverage

## Contributor credit
- substantive bugfix 
- small follow-up TLS consistency fix added on top during salvage

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_email.py`