**fix(feishu): finalize remote document downloads inside httpx.AsyncClient context**

## Summary

Feishu outbound document fetch (`_download_remote_document`) previously read `response.headers` / `response.content` **after** exiting `async with httpx.AsyncClient(...)`. That can leave pooled HTTP connections in an awkward shutdown window and adds avoidable pressure on process file descriptors in long-running gateways ().

This change snapshots `Content-Type` and the response body **while the client context is still active**, then passes bytes into `cache_document_from_bytes`.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_feishu.py`