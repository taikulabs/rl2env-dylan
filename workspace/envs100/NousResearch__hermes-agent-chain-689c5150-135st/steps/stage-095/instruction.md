**fix(gateway): fix matrix lingering typing indicator**

## What does this PR do?

Fixes the Matrix typing indicator lingering for ~30 seconds after Hermes has already sent a response.

Matrix typing events were sent with a `30000` ms timeout, but the Matrix adapter inherited the base `stop_typing()` no-op. As a result, cleanup calls after agent completion did not send a “typing stopped” event, so Matrix clients kept showing Hermes as typing until the timeout expired.

This PR adds a Matrix-specific `stop_typing()` implementation that calls `set_typing(..., timeout=0)`, which `mautrix` sends as `typing: false`.

**Testing**

```bash
python -m pytest tests/gateway/test_matrix.py -q
```

Result:

```text
112 passed in 1.57s
```

## Related Issue