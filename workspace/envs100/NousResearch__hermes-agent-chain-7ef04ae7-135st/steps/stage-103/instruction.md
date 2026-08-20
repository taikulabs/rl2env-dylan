**feat(lsp): add PowerShellEditorServices language server**

## Summary
Hermes now provides semantic diagnostics for PowerShell files (`.ps1` / `.psm1` / `.psd1`) by wiring [PowerShellEditorServices](https://github.com/PowerShell/PowerShellEditorServices) into the LSP server registry.

PSES is not a single PATH binary — it's a PowerShell module bundle launched by a `pwsh`/`powershell` host via `Start-EditorServices.ps1`. It ships as a GitHub release zip (no npm/go/pip recipe), so it sits in the **manual install tier** alongside `rust-analyzer` and `clangd`.

## Changes
- `agent/lsp/servers.py`: register the `powershell` server — extensions, `powershell` language IDs, a root resolver (PSScriptAnalyzer settings → git workspace), a bundle-locator, and a stdio spawn builder that launches `pwsh -NoProfile -NonInteractive ... Start-EditorServices.ps1 -Stdio`.
- `agent/lsp/install.py`: manual-tier recipe so `hermes lsp status`/`list` report it (probes the `pwsh` host).
- `website/docs/user-guide/features/lsp.md`: supported-servers row + a PowerShell setup section.
- `tests/agent/lsp/test_powershell_server.py`: 8 tests (routing, language IDs, skip-without-pwsh, skip-without-bundle, command construction, override precedence, `bundlePath` not leaked into init options).

Bundle resolution order: `lsp.servers.powershell.command` override → init `bundlePath` → `PSES_BUNDLE_PATH` env → `<HERMES_HOME>/lsp/PowerShellEditorServices`.

## Validation
| | Result |
|---|---|
| New tests | 8 passed |
| Full LSP suite | 153 passed |
| E2E (real imports, isolated HERMES_HOME) | `.ps1/.psm1/.psd1` route to `powershell`, spawn command built correctly, `lsp status` → `installed` once `pwsh` found |

## Infographic
![PowerShell LSP](https://v3b.fal.media/files/b/0aa06d75/qeALc_D6Q7SWONkATyBwU_5hQ1eT5O.png)

Nous Research

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/lsp/test_powershell_server.py`