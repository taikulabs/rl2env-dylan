**fix(file_tools): block /private/etc writes on macOS symlink bypass**

## Summary

 — on macOS, `/etc` is a symlink to `/private/etc`. `os.path.realpath()` resolves `/etc/hosts` → `/private/etc/hosts`, which bypassed the `/etc/` prefix in `_SENSITIVE_PATH_PREFIXES`.

### Changes
- Add `/private/etc/` and `/private/var/` to `_SENSITIVE_PATH_PREFIXES`
- Check both `realpath`-resolved and `normpath`-normalized paths against the blocklist
- Add regression tests for the macOS symlink bypass

### What was NOT changed
`_is_write_denied()` in `file_operations.py` already works correctly on macOS because both `WRITE_DENIED_PATHS` and `WRITE_DENIED_PREFIXES` are constructed using `os.path.realpath()` at module load time. No changes needed there.

### Attribution