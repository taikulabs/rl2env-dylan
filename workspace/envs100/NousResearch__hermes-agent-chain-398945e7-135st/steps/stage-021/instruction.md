**fix(ci): stabilize main test suite regressions**

## What does this PR do?

Stabilizes the Hermes Agent main test suite so blocked PRs can be validated against a green base again.

The failures were mostly caused by host state, import-order state, and xdist ordering leaks. This PR hardens those paths so tests do not depend on a developer machine profile, local terminal state, current environment variables, `TERM`, or stale process-global state from earlier tests.

It also fixes a real streaming interrupt race surfaced by CI: if the worker thread observes `_interrupt_requested` before the outer polling loop does, the interrupt is now propagated through the normal result channel instead of becoming an unhandled thread exception.

This intentionally keeps the Codex Responses tool-call history fix out of this branch. That work remains in PR #17645.

## Related Issue

No linked GitHub issue.

Replacement path for the closed, unmerged #17618 CI-stabilization PR.

Related PR: #17645 remains separate for Codex Responses tool-call history sanitization.