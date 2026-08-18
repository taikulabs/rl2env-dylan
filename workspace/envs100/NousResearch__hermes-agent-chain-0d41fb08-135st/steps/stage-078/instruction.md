**fix: fall back to default certs when CA bundle path doesn't exist**

## Summary

`_resolve_verify()` in `hermes_cli/auth.py` returned CA bundle file paths without checking if the file exists. When a user logs into Nous Portal on their host machine (where `SSL_CERT_FILE` points to a valid cert bundle), that path gets persisted in `auth.json`'s `tls.ca_bundle`. Running `hermes model` later inside a Docker container — where the host path doesn't exist — caused:

```
Could not verify credentials: [Errno 2] No such file or directory
```

### Fix

Added a file existence check in `_resolve_verify()`. When the resolved CA bundle path doesn't exist, logs a warning and falls back to `True` (default certifi-based TLS verification). This is safe because TLS is still verified — just using bundled certs instead of a stale path.

### Changes
- `hermes_cli/auth.py`: 8-line guard in `_resolve_verify()`
- `tests/hermes_cli/test_auth_nous_provider.py`: 8 new test cases covering all CA bundle sources (auth state, env vars, explicit param) with both missing and valid paths