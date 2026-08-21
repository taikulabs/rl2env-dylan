**feat(agent): expose coding-context project facts (project.facts RPC)**

## Summary
Follow-up to the coding-context posture. That PR already detects each repo's verify loop — manifests, package manager (lockfile sniff), the exact test/lint/build commands, context files — and bakes it into the system-prompt snapshot. But it's a **string for the model only**; non-prompt consumers (the desktop verify UI) had no way to read it without re-sniffing and drifting from the prompt.

This splits **detection from rendering**, keeping one source of truth:

- `detect_project_facts(root) -> ProjectFacts` (frozen dataclass) holds the structured facts.
- `_project_facts()` now *renders* that into the same snapshot lines — the prompt block stays **byte-identical** (cache-safe).
- `project_facts_for(cwd)` resolves the workspace root (git, else marker) and returns the structured facts, or `None` outside a workspace.
- `project.facts` gateway RPC surfaces it to any client (desktop / TUI / ACP).

No behavior change to the prompt; this is purely an extraction + a read-only RPC. It unblocks a desktop "one-click verify + last-status" surface that consumes the agent's already-computed facts instead of duplicating "are we coding?" / verify-command logic.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_coding_context.py`