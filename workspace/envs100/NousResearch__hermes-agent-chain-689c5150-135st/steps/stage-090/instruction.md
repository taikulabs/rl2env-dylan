**feat(doctor): add Command Installation check for hermes bin symlink**

## Summary

`hermes doctor` now includes a **◆ Command Installation** section that checks whether the `~/.local/bin/hermes` symlink exists and points to the correct venv entry point. With `--fix`, it creates or repairs the symlink automatically.

**Addresses user report:** `python -m hermes_cli.main` doesn't have an option to fix a broken local bin install, and re-installing doesn't fix it. The issue is that `pip install -e .` regenerates the venv entry point but doesn't touch the `~/.local/bin/hermes` symlink.

## What it checks

- ✓ Venv entry point exists (`venv/bin/hermes` or `.venv/bin/hermes`)
- ✓ Symlink at `~/.local/bin/hermes` (or `$PREFIX/bin/hermes` on Termux) exists
- ✓ Symlink points to the correct target
- ⚠ PATH includes `~/.local/bin` (warns if not)
- Skips on Windows (different mechanism)

## --fix behavior

- Creates missing symlink (and parent dirs)
- Repairs symlink pointing to wrong target
- Warns about PATH if `~/.local/bin` is not on PATH (manual fix — can't auto-edit shell config)

## Changes

| File | Change |
|------|--------|
| `hermes_cli/doctor.py` | New ◆ Command Installation section (+82 lines) |
| `tests/hermes_cli/test_doctor_command_install.py` | 10 new tests (all scenarios) |