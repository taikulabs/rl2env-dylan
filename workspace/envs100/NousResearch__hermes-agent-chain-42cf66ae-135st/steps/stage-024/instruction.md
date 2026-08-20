**fix: stop local terminal warning without minisweagent**

## Summary
- make local terminal requirement checks use Hermes' local backend instead of importing `minisweagent`
- add a regression test covering `TERMINAL_ENV=local` when `minisweagent` is not importable
- verify the repeated startup warning is gone in a live `hermes chat -q` run

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_terminal_requirements.py`