**feat(discord): add document caching and text-file injection**

## Summary

Brings Discord's document handling in line with Telegram, Slack, Signal, Mattermost, and Email adapters. Discord was the only platform still passing expiring CDN URLs through instead of caching documents locally.

### What changed
- Documents (.pdf, .docx, .xlsx, .pptx, .txt, .md) are downloaded and cached locally
- .txt and .md files under 100KB have content injected directly into event.text
- Unsupported file types (.zip etc.) are now correctly skipped instead of being misclassified as DOCUMENT
- 9 new tests covering all edge cases

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_discord_document_handling.py`