**fix(debug): redact log content at upload time in hermes debug share**

## What does this PR do?

Closes a public-leak path: `hermes debug share` uploads logs to paste.rs / dpaste.com per the bug-report templates' explicit instructions, but never applies `redact_sensitive_text` before upload. With `security.redact_secrets` off by default after #16794, those uploads have been carrying credentials onto a public paste service.

This PR applies `agent.redact.redact_sensitive_text(text, force=True)` to log content at the `_capture_log_snapshot` boundary, before it reaches `upload_to_pastebin`. On-disk logs are not modified. A visible banner is prepended to each upload-bound log paste so reviewers know redaction was applied. A `--no-redact` flag preserves deliberate unredacted sharing for maintainer-coordinated cases.

`force=True` is non-negotiable: without it, `redact_sensitive_text` short-circuits at `agent/redact.py:322` when `HERMES_REDACT_SECRETS` is unset, so the fix would silently be a no-op for its target audience. The regression test `TestCaptureLogSnapshotRedaction::test_force_true_overrides_unset_env_var` pins this down so a future refactor cannot accidentally drop it.

This is upload-time-only, not local-disk redaction. It does not change `security.redact_secrets` defaults; it closes the public-leak path that is structurally upstream of the local-redaction question.

## Related Issue

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_debug.py`