**fix(setup): auto-install matrix-nio during hermes setup**

## Summary

Salvaged from PR #1978 by @Gutslabs and PR #1979 by @cutepawss — applied onto current main with authorship preserved.

Setup previously only printed a manual install hint for `matrix-nio`, causing the gateway to crash with "matrix-nio not installed" after configuring Matrix. Now auto-installs the package during setup.

**Changes:**

- **`hermes_cli/setup.py`** — Replaces the manual hint with auto-install logic using the same uv-first/pip-fallback pattern as Daytona and Modal backends. Installs `matrix-nio[e2e]` when E2EE is enabled, plain `matrix-nio` otherwise. (from #1978)
- **`pyproject.toml`** — Adds `hermes-agent[matrix]` to the `[all]` extra so `pip install hermes-agent[all]` includes it. (from #1978 and #1979)
- **`tests/test_project_metadata.py`** — Regression test ensuring `hermes-agent[matrix]` stays in the `[all]` group. (from #1979)

,