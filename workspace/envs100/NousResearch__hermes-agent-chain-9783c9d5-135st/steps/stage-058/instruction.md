**feat(api-server): add Access-Control-Max-Age to CORS preflight (salvage #3514)**

## Summary
Adds `Access-Control-Max-Age: 600` to CORS preflight responses in the API server gateway adapter. Browsers cache the preflight for 10 minutes, reducing redundant OPTIONS requests.

Salvaged from #3514 by @aydnOktay — cherry-picked onto current main with authorship preserved.

## Changes
- Added `Access-Control-Max-Age: 600` in both wildcard and specific-origin CORS branches
- Added test verifying the header is set on preflight responses

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_api_server.py`