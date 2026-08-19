**fix: allow agent-created skills with caution-level findings**



Changes the agent-created install policy from `(allow, block, block)` to `(allow, allow, block)` — matching the trusted policy. Caution-level findings (Docker refs, pip install, git clone) no longer block agent-created skills. Critical findings (exfiltration, prompt injection, reverse shells) remain blocked.

Adds 4 tests for agent-created policy coverage. All 53 guard tests pass.
