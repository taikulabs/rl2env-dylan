**fix(cli): prefer curses over simple_term_menu in setup.py**

## Summary
- replace `simple_term_menu` usage in `hermes_cli/setup.py` with curses-based and numbered-fallback flows
- route checklist prompts through the shared curses checklist helper already used elsewhere in the CLI
- add focused regression tests for setup prompt behavior

## Notes
- salvages the substantive intent from PR #1462 onto current `main`
- avoids the stale/mismatched PR body and keeps the change tightly scoped to setup prompt handling