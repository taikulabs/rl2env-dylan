**fix(gateway): default group sessions to per-user isolation**

## Summary
- default group and channel chats to per-user session isolation when the platform provides a participant id
- add `group_sessions_per_user` in `config.yaml` so operators can opt back into a shared room session
- thread the setting through gateway session keys, interrupt handling, adapter-side batching, and session store lookup
- expand docs for Discord gateway behavior, session routing, concurrency, and the new config knob

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_config.py`
- `tests/gateway/test_session.py`