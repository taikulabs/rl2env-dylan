**fix(security): block gateway and tool env vars in subprocesses**

## Summary
- extend subprocess env sanitization beyond provider credentials so Hermes-managed tool, messaging, and related gateway runtime vars are stripped before local/background subprocesses launch
- reuse one sanitizer in both LocalEnvironment and ProcessRegistry so PTY and non-PTY background processes honor the same blocklist and _HERMES_FORCE_ escape hatch
- add regression coverage for local terminal execution, blocklist coverage drift, and process_registry spawning

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_local_env_blocklist.py`
- `tests/tools/test_process_registry.py`