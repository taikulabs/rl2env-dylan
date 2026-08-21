**fix(gateway): redact credentials from approval prompt before sending to chat platform**

## Summary

 — a credential-egress bug in the gateway approval path.

When Tirith flags a command for a credential-shaped pattern, its own *finding*
is redacted (it reports that a pattern matched, not the value). But
`_approval_notify_sync` in `gateway/run.py` builds the operator approval prompt
from the **raw** `approval_data["command"]` string and passes it straight into
both the button-based path (`send_exec_approval(command=cmd, ...)`) and the
plain-text `/approve` fallback — so the exact secret Tirith just decided to
withhold is sent verbatim to the chat platform (Telegram/Discord/Slack/etc.),
undoing the redaction one layer up.

Verified still present on current `main` (`b4cb33cd4`): the approval closure
reads `cmd = approval_data.get("command", "")` and never redacts before send.

## Fix

Redact the command via `redact_sensitive_text(cmd, force=True)` — the same
Tirith-grade redactor — **before** it reaches either send path. `force=True`
so the approval prompt (a hard secret-egress boundary) honors redaction even
when `security.redact_secrets` is disabled. Clean commands pass through
unchanged, so the operator can still judge the action.

## Salvage / attribution

Salvaged from #48462 (@liuhao1024), cherry-picked onto current `main`; authored
by @liuhao1024.

Test-hardening folded in (co-authored): the original tests only exercised
`redact_sensitive_text` in isolation (a change-detector — they'd pass even if
the production redaction call were deleted). This version extracts the wiring
into a module-level `_redact_approval_command()` seam (the call site is a deeply
nested gateway closure that can't be driven directly) and the tests now:
- bind that production seam with the issue's real credential patterns (PAT,
  OpenAI key, bearer token), incl. a `force`-overrides-disabled case;
- assert `_approval_notify_sync` routes the command through the seam **before**
  `send_exec_approval` receives it.
Both behaviors are mutation-checked (neutering the seam fails the redaction
tests; removing the wiring call fails the ordering guard).

## Tests

`tests/gateway/test_approval_prompt_redaction.py` (7) pass; 37 passed across the
approval test surface (`test_slack_approval_buttons`, `test_matrix_exec_approval`,
`test_approval_interrupt`) — no regression from the seam extraction.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_approval_prompt_redaction.py`