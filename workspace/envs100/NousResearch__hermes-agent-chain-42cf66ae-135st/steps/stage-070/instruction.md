**fix(gateway): fall back to module entrypoint when hermes is not on PATH**

## Summary
- salvage PR #1052 onto current main by cherry-picking the contributor's /update path-resolution fix with authorship preserved
- fall back to the current interpreter module entrypoint when the hermes shim is missing from PATH
- resolve the current-main conflict by preserving the newer gateway lifecycle logic and adapting the fallback to use shell-quoted argv parts safely
- add/update gateway /update tests covering the fallback resolution behavior