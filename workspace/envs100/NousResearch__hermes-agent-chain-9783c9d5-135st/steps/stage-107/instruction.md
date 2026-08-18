**fix(cli): add missing subprocess.run() timeouts in doctor and status**

4 `subprocess.run()` calls in CLI utilities had no timeout and could hang indefinitely:

- `docker info` → **+timeout=10** (daemon unresponsive)
- `ssh ... echo ok` → **+timeout=15** (host unreachable past ConnectTimeout)
- `systemctl --user is-active` → **+timeout=5** (D-Bus stuck)
- `launchctl list` → **+timeout=5** (local, should be instant)

Each catches `TimeoutExpired` and treats as failure, consistent with existing patterns. Includes AST-based regression test that ensures all `subprocess.run()` calls across 4 CLI modules have timeout params.

**E2E verified:** AST scan confirms all 5 `subprocess.run()` calls in doctor.py/status.py have timeouts. 28 doctor/status tests + 4 new regression tests pass.

Cherry-picked from PR #3693 by @dieutx with authorship preserved.