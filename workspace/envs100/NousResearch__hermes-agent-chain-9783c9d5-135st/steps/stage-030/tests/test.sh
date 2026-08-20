#!/bin/bash
# Harbor step verifier. Placeholders are substituted by _pr_chain_steps.py
# via string.Template; every literal shell dollar is written as $ here.
#          toolchain PATH prefix (may be empty)
#   pytest -v -n 0 tests/gateway/test_media_download_retry.py          the test command chain
#   pytest -v -n 0 tests/gateway/test_media_download_retry.py  the same chain, single-quote-escaped for --test-cmds
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
( pytest -v -n 0 tests/gateway/test_media_download_retry.py ) > /logs/verifier/test_output.log 2>&1
TEST_EXIT_CODE=$?
cat /logs/verifier/test_output.log
# Cumulative check: replay earlier stages' graded tests (a separate
# diagnostic run; it never gates the local reward).
if [ -d "$SCRIPT_DIR/regression/files" ]; then
  (cd "$SCRIPT_DIR/regression/files" && find . -type f -print0) | \
    while IFS= read -r -d "" rel; do
      mkdir -p "/workspace/$(dirname "$rel")"
      cp "$SCRIPT_DIR/regression/files/$rel" "/workspace/$rel"
    done
fi
( pytest -v -n 0 tests/agent/test_auxiliary_client.py tests/agent/test_prompt_builder.py tests/gateway/test_agent_cache.py tests/gateway/test_api_server_toolset.py tests/gateway/test_dm_topics.py tests/gateway/test_flush_memory_stale_guard.py tests/gateway/test_reasoning_command.py tests/gateway/test_send_retry.py tests/gateway/test_session.py tests/gateway/test_session_info.py tests/gateway/test_session_race_guard.py tests/gateway/test_telegram_network_reconnect.py tests/gateway/test_verbose_command.py tests/hermes_cli/test_commands.py tests/hermes_cli/test_sessions_delete.py tests/hermes_cli/test_setup_openclaw_migration.py tests/hermes_cli/test_skills_hub.py tests/hermes_cli/test_tools_config.py tests/test_anthropic_adapter.py tests/test_cli_init.py tests/test_cli_status_bar.py tests/test_compressor_fallback_update.py tests/test_crossloop_client_cache.py tests/test_exit_cleanup_interrupt.py tests/test_hermes_state.py tests/test_provider_parity.py tests/test_session_reset_fix.py tests/tools/test_approval.py tests/tools/test_session_search.py tests/tools/test_skills_guard.py tests/tools/test_skills_hub.py ) > /logs/verifier/regression_output.log 2>&1 || true
cat /logs/verifier/regression_output.log
# -S keeps agent-planted sitecustomize.py/.pth files out of the grader.
python3 -S "$SCRIPT_DIR/verifier.py" \
  --log /logs/verifier/test_output.log \
  --f2p "$SCRIPT_DIR/f2p.json" --p2p "$SCRIPT_DIR/p2p.json" \
  --test-cmds 'pytest -v -n 0 tests/gateway/test_media_download_retry.py' --exit-code "$TEST_EXIT_CODE" \
  --require-clean-command --regression "$SCRIPT_DIR/regression.json" --regression-log /logs/verifier/regression_output.log \
  --out-dir /logs/verifier || \
  echo "0.0" > /logs/verifier/reward.txt
# reward.txt is the verdict, not this script's exit code.
exit 0
