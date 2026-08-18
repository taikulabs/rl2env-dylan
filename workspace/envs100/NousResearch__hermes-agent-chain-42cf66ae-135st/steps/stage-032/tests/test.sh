#!/bin/bash
set -uxo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd /workspace
git config --global --add safe.directory /workspace
mkdir -p /logs/verifier
# Kill agent-spawned background processes before grading: after the
# agent phase they are orphaned onto PID 1, while this script's own
# process tree is not. A leftover loop could otherwise rewrite
# /logs/verifier/reward.txt after the verifier writes it.
for status in /proc/[0-9]*/status; do
  pid="${status#/proc/}"; pid="${pid%/status}"
  ppid="$(awk '/^PPid:/{print $2}' "$status" 2>/dev/null)"
  if [ "$ppid" = "1" ] && [ "$pid" != "1" ]; then kill -9 "$pid" 2>/dev/null || true; fi
done
# Purge planted conftest.py files on the graded collection path, then
# restore the gold harness (tests, conftests, pytest config) over
# whatever the agent left behind.
rm -f "/workspace/conftest.py"
rm -f "/workspace/tests/conftest.py"
rm -f "/workspace/tests/hermes_cli/conftest.py"
if [ -d "$SCRIPT_DIR/files" ]; then
  (cd "$SCRIPT_DIR/files" && find . -type f -print0) | \
    while IFS= read -r -d "" rel; do
      mkdir -p "/workspace/$(dirname "$rel")"
      cp "$SCRIPT_DIR/files/$rel" "/workspace/$rel"
    done
fi
( pytest -v -n 0 tests/hermes_cli/test_setup_noninteractive.py tests/hermes_cli/test_setup_openclaw_migration.py ) > /logs/verifier/test_output.log 2>&1
TEST_EXIT_CODE=$?
cat /logs/verifier/test_output.log
# -S keeps agent-planted sitecustomize.py/.pth files out of the grader.
python3 -S "$SCRIPT_DIR/verifier.py" \
  --log /logs/verifier/test_output.log \
  --f2p "$SCRIPT_DIR/f2p.json" --p2p "$SCRIPT_DIR/p2p.json" \
  --test-cmds 'pytest -v -n 0 tests/hermes_cli/test_setup_noninteractive.py tests/hermes_cli/test_setup_openclaw_migration.py' --exit-code "$TEST_EXIT_CODE" \
  --out-dir /logs/verifier || \
  echo "0.0" > /logs/verifier/reward.txt
# reward.txt is the verdict, not this script's exit code.
exit 0
