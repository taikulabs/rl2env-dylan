**fix(security): catch sensitive path writes in approval checks**

Salvage of #1934 by @Gutslabs onto current main.

## Summary

Extends dangerous command detection to catch writes to sensitive paths via shell variable expansions (`$HOME`, `$HERMES_HOME`, `${HOME}`) and redirect operators (`>`, `>>`).

### Previously missed (now caught)
- `echo x | tee $HERMES_HOME/.env`
- `echo x | tee "$HERMES_HOME/.env"`
- `echo x > $HERMES_HOME/.env`
- `cat key >> $HOME/.ssh/authorized_keys`
- `cat key >> ~/.ssh/authorized_keys`

### Changes
- Consolidated `_SENSITIVE_WRITE_TARGET` regex covering `/etc/`, `/dev/sd`, SSH paths (`~/.ssh/`, `$HOME/.ssh/`), and HERMES `.env` (`~/.hermes/.env`, `$HOME/.hermes/.env`, `$HERMES_HOME/.env`)
- Updated `tee` pattern to use consolidated target
- New redirect pattern catches `>` / `>>` writes to sensitive paths
- 7 new regression tests + safe-write negative case

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_approval.py`