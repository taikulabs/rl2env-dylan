**feat: add `hermes debug share` — upload debug report to pastebin**

## Summary

Adds `hermes debug share` — collects system info + recent logs and uploads to a paste service, returning a shareable URL for support.

**Usage:**
```
hermes debug share              # Upload and print URL
hermes debug share --lines 500  # Include more log lines
hermes debug share --expire 30  # Keep paste for 30 days (dpaste.com only)
hermes debug share --local      # Print locally without uploading
```

**Example output:**
```
Collecting debug report...
Uploading...

Debug report uploaded:
  https://paste.rs/39twB

Share this link with the Hermes team for support.
```

## What's in the report

Reuses `hermes dump` output (system info, config with secrets redacted, API key status, features, config overrides) plus tails of:
- agent.log (last 200 lines)
- errors.log (last 100 lines)
- gateway.log (last 100 lines)

## Paste services

- **Primary:** paste.rs (simple, fast, no auth)
- **Fallback:** dpaste.com (supports expiry)
- If both fail, prints the report locally so the user can paste manually

## Files changed

| File | Change |
|------|--------|
| `hermes_cli/debug.py` | New module — paste upload helpers + report collection |
| `hermes_cli/main.py` | Wire `cmd_debug` + argparse subparser |
| `tests/hermes_cli/test_debug.py` | 19 tests covering upload, collection, CLI routing |