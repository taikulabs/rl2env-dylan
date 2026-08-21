#!/bin/bash
# Harbor step verifier. Placeholders are substituted by _pr_chain_steps.py
# via string.Template; every literal shell dollar is written as $ here.
#          toolchain PATH prefix (may be empty)
#   pytest -v -n 0 tests/agent/test_curator_activity.py tests/hermes_cli/test_curator_status.py tests/tools/test_skill_usage.py          the test command chain
#   pytest -v -n 0 tests/agent/test_curator_activity.py tests/hermes_cli/test_curator_status.py tests/tools/test_skill_usage.py  the same chain, single-quote-escaped for --test-cmds
# Repo-derived file paths never appear here; the purge list rides in
# tests/purge.manifest (NUL-delimited) and is read below with read -d ''.
set -uxo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd /workspace || exit 1
git config --global --add safe.directory /workspace
mkdir -p /logs/verifier
# A degraded carry (partially applied at setup) means the tree was never
# oracle-validated in this state. That is an infrastructure failure, not an
# agent result: score 0, flag it for the trainer, and do not grade the tree.
if [ -f /workspace/.r2e_carry_degraded.json ]; then
  cp /workspace/.r2e_carry_degraded.json /logs/verifier/carry_degraded.json
  echo '{"reward": 0.0, "invalid_transition": 1.0}' > /logs/verifier/reward.json
  echo "0.0" > /logs/verifier/reward.txt
  python3 -S - <<'PYEOF'
import json
details = {
    "reward": 0.0,
    "invalid_transition": True,
    "reason": "carry patch applied with rejects; tree never oracle-validated",
    "parse_status": "not_run_invalid_transition",
}
with open("/logs/verifier/reward-details.json", "w") as f:
    json.dump(details, f, indent=2)
PYEOF
  exit 0
fi
# Purge harness files the gold tree does not provide (a planted conftest.py
# or pytest.ini can fabricate results), then restore the gold harness over
# whatever the agent left behind.
if [ -f "$SCRIPT_DIR/purge.manifest" ]; then
  while IFS= read -r -d "" rel; do
    rm -f -- "/workspace/$rel"
  done < "$SCRIPT_DIR/purge.manifest"
fi
if [ -d "$SCRIPT_DIR/files" ]; then
  (cd "$SCRIPT_DIR/files" && find . -type f -print0) | \
    while IFS= read -r -d "" rel; do
      mkdir -p "/workspace/$(dirname "$rel")"
      cp "$SCRIPT_DIR/files/$rel" "/workspace/$rel"
    done
fi
# The graded run executes agent code, so it runs UNPRIVILEGED: nobody cannot
# read or write the reward channel, which is locked to root first. pytest
# imports agent modules at collection time, and import-time side effects then
# run as nobody too. The a+rX/a+rwX sweeps are required: this repo's tests
# read the real home directory (~/.hermes config, and /root is 700 by default)
# and write log/scratch dirs inside the workspace and home. No exposure is
# anything in these trees was already readable to the agent (root) in its own
# phase, and the reward channel stays root-only.
chmod 700 /logs/verifier
chmod -R a+rwX /root 2>/dev/null || true
chmod -R a+rX /opt/venv 2>/dev/null || true
chmod -R a+rwX /workspace 2>/dev/null || true
rm -f /tmp/r2e_ctrf.json /tmp/r2e_regression_ctrf.json
( setpriv --reuid nobody --regid nogroup --clear-groups --no-new-privs \
  env PYTHONDONTWRITEBYTECODE=1 bash -c 'pytest -v -n 0 tests/agent/test_curator_activity.py tests/hermes_cli/test_curator_status.py tests/tools/test_skill_usage.py --ctrf /tmp/r2e_ctrf.json -p no:cacheprovider' \
) > /logs/verifier/test_output.log 2>&1
TEST_EXIT_CODE=$?
cat /logs/verifier/test_output.log
cp /tmp/r2e_ctrf.json /logs/verifier/ctrf.json 2>/dev/null || true
# Cumulative check: replay earlier stages' graded tests (a separate
# diagnostic run; it never gates the local reward).
if [ -d "$SCRIPT_DIR/regression/files" ]; then
  (cd "$SCRIPT_DIR/regression/files" && find . -type f -print0) | \
    while IFS= read -r -d "" rel; do
      mkdir -p "/workspace/$(dirname "$rel")"
      cp "$SCRIPT_DIR/regression/files/$rel" "/workspace/$rel"
    done
fi
setpriv --reuid nobody --regid nogroup --clear-groups --no-new-privs \
  env PYTHONDONTWRITEBYTECODE=1 bash -c 'pytest -v -n 0 tests/acp_adapter/test_acp_images.py tests/agent/test_curator_classification.py tests/agent/test_curator_reports.py tests/test_tui_gateway_server.py tests/tools/test_file_sync_back.py tests/tools/test_skill_usage.py --ctrf /tmp/r2e_regression_ctrf.json -p no:cacheprovider' \
  > /logs/verifier/regression_output.log 2>&1
REGRESSION_EXIT_CODE=$?
cat /logs/verifier/regression_output.log
cp /tmp/r2e_regression_ctrf.json /logs/verifier/regression_ctrf.json 2>/dev/null || true
# -S keeps agent-planted sitecustomize.py/.pth files out of the grader.
python3 -S "$SCRIPT_DIR/verifier.py" \
  --log /logs/verifier/test_output.log \
  --f2p "$SCRIPT_DIR/f2p.json" --p2p "$SCRIPT_DIR/p2p.json" \
  --test-cmds 'pytest -v -n 0 tests/agent/test_curator_activity.py tests/hermes_cli/test_curator_status.py tests/tools/test_skill_usage.py' --exit-code "$TEST_EXIT_CODE" \
  --ctrf /logs/verifier/ctrf.json \
  --require-clean-command --regression "$SCRIPT_DIR/regression.json" --regression-log /logs/verifier/regression_output.log --regression-exit-code "$REGRESSION_EXIT_CODE" --regression-ctrf /logs/verifier/regression_ctrf.json \
  --out-dir /logs/verifier || \
  echo "0.0" > /logs/verifier/reward.txt
# reward.txt is the verdict, not this script's exit code.
exit 0
