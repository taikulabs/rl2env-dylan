**fix(browser): preserve agent-browser paths with spaces**

## Summary
- preserve local `agent-browser` executable paths as a single argv entry so installs under paths with spaces still work
- keep the `npx agent-browser` fallback behavior unchanged by splitting only that synthetic command form
- add regression tests covering both spaced executable paths and the `npx` fallback

## Verification
- `py -3 -m pytest -o addopts= tests/tools/test_browser_homebrew_paths.py::TestRunBrowserCommandPathConstruction::test_subprocess_preserves_executable_path_with_spaces tests/tools/test_browser_homebrew_paths.py::TestRunBrowserCommandPathConstruction::test_subprocess_splits_npx_fallback_into_command_and_package -q`

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_browser_homebrew_paths.py`