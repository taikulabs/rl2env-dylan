**fix(tools): neutralize shell injection in _write_to_sandbox via path quoting**

## Summary

`_write_to_sandbox` in `tools/tool_result_storage.py` interpolated `storage_dir` and `remote_path` directly into a shell command passed to `env.execute()`. If either path contained shell metacharacters (spaces, semicolons, \$(), backticks), the result was arbitrary command execution inside the sandbox.

**Before:**
```python
f"mkdir -p {storage_dir} && cat > {remote_path} << '{marker}'"
```

**After:**
```python
f"mkdir -p {shlex.quote(storage_dir)} && cat > {shlex.quote(remote_path)} << '{marker}'"
```

`shlex.quote()` leaves clean paths (alphanumeric + slashes/hyphens/dots/underscores) unmodified, so existing behavior is unchanged. Paths with unsafe characters get single-quoted.

The heredoc body was already safe (single-quoted delimiter prevents shell expansion).

## Changes

- `tools/tool_result_storage.py`: added `import shlex`, quoted both path interpolations
- `tests/tools/test_tool_result_storage.py`: 3 new tests covering spaces, \$(command) substitution, and semicolon injection