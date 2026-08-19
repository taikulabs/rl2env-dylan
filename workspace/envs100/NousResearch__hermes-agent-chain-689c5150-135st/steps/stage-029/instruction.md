**fix(backup): correct marker filenames in _validate_backup_zip**

## What does this PR do?

Fixes a bug in `hermes_cli/backup.py` where `_validate_backup_zip` checked for database filenames that do not exist in a real Hermes installation, causing valid backups to be silently rejected on import.