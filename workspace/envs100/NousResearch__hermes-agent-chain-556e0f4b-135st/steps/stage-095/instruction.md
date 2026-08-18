**fix: expand tilde (~) in vision_analyze local file paths**

## Summary

`vision_analyze` failed when given paths like `~/image.png` because `Path('~/...')` doesn't expand tilde. The tool fell through to URL validation, producing a confusing error: *Invalid image source*.

## Fix

One-line change: wrap with `os.path.expanduser()` before constructing the `Path` object (line 245 of `vision_tools.py`).

## Tests

Added two tests:
- **`test_tilde_path_expanded_to_local_file`** — verifies `~/image.png` resolves and analyzes successfully
- **`test_tilde_path_nonexistent_file_gives_error`** — verifies graceful error for `~/nonexistent.png`

All 45 vision tool tests pass.