**fix(security): block gateway and tool env vars in subprocesses**

## Summary
- extend subprocess env sanitization beyond provider credentials so Hermes-managed tool, messaging, and related gateway runtime vars are stripped before local/background subprocesses launch
- reuse one sanitizer in both LocalEnvironment and ProcessRegistry so PTY and non-PTY background processes honor the same blocklist and _HERMES_FORCE_ escape hatch
- add regression coverage for local terminal execution, blocklist coverage drift, and process_registry spawning