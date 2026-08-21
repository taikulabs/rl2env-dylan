#!/bin/bash
# Harbor step verifier. Placeholders are substituted by _pr_chain_steps.py
# via string.Template; every literal shell dollar is written as $ here.
#          toolchain PATH prefix (may be empty)
#   pytest -v -n 0 tests/gateway/test_config.py          the test command chain
#   pytest -v -n 0 tests/gateway/test_config.py  the same chain, single-quote-escaped for --test-cmds
# Repo-derived file paths never appear here; the purge list rides in
# tests/purge.manifest (NUL-delimited) and is read below with read -d ''.
set -uxo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd /workspace || exit 1
git config --global --add safe.directory /workspace
mkdir -p /logs/verifier
# A degraded carry (merged with rejects at setup) is telemetry, not a veto:
# the tree is graded by its tests either way, and the flag lets trainers
# exclude such steps. Measured: invalidating on agent-vs-churn conflicts made
# the environment unplayable (Opus 0.03 over 33 steps; oracle ~1.0).
DEGRADED_FLAG=""
if [ -f /workspace/.r2e_carry_degraded.json ]; then
  cp /workspace/.r2e_carry_degraded.json /logs/verifier/carry_degraded.json
  DEGRADED_FLAG="--carry-degraded"
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
  env PYTHONDONTWRITEBYTECODE=1 bash -c 'pytest -v -n 0 tests/gateway/test_config.py --ctrf /tmp/r2e_ctrf.json -p no:cacheprovider' \
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
  env PYTHONDONTWRITEBYTECODE=1 bash -c 'pytest -v -n 0 tests/acp_adapter/test_acp_images.py tests/agent/test_anthropic_adapter.py tests/agent/test_context_compressor.py tests/agent/test_curator.py tests/agent/test_curator_activity.py tests/agent/test_curator_classification.py tests/agent/test_curator_reports.py tests/agent/test_error_classifier.py tests/agent/test_kimi_coding_anthropic_thinking.py tests/agent/test_onboarding.py tests/agent/test_skill_commands_reload.py tests/agent/transports/test_chat_completions.py tests/cli/test_cli_reload_skills.py tests/cli/test_cli_terminal_response_sanitizer.py tests/cron/test_scheduler.py tests/gateway/test_api_server.py tests/gateway/test_api_server_runs.py tests/gateway/test_approve_deny_commands.py tests/gateway/test_busy_session_auth_bypass.py tests/gateway/test_pending_drain_no_recursion.py tests/gateway/test_platform_base.py tests/gateway/test_reload_skills_command.py tests/gateway/test_send_multiple_images.py tests/gateway/test_session_boundary_security_state.py tests/gateway/test_signal.py tests/gateway/test_telegram_approval_buttons.py tests/gateway/test_telegram_documents.py tests/gateway/test_tts_media_routing.py tests/gateway/test_unauthorized_dm_behavior.py tests/hermes_cli/test_curator_status.py tests/hermes_cli/test_dashboard_lifecycle_flags.py tests/hermes_cli/test_gateway.py tests/hermes_cli/test_mcp_reload_confirm_gate.py tests/hermes_cli/test_plugins.py tests/hermes_cli/test_set_config_value.py tests/hermes_cli/test_setup_openclaw_migration.py tests/hermes_cli/test_update_stale_dashboard.py tests/hermes_cli/test_user_providers_model_switch.py tests/openviking_plugin/test_openviking.py tests/run_agent/test_deepseek_reasoning_content_echo.py tests/run_agent/test_run_agent.py tests/run_agent/test_tool_executor_contextvar_propagation.py tests/test_get_tool_definitions_cache_isolation.py tests/test_model_tools.py tests/test_tui_gateway_server.py tests/tools/test_delegate.py tests/tools/test_file_sync_back.py tests/tools/test_skill_manager_tool.py tests/tools/test_skill_usage.py tests/tools/test_slash_confirm.py tests/tools/test_tts_command_providers.py tests/tools/test_tts_mistral.py tests/tools/test_tts_piper.py tests/tui_gateway/test_review_summary_callback.py --ctrf /tmp/r2e_regression_ctrf.json -p no:cacheprovider' \
  > /logs/verifier/regression_output.log 2>&1
REGRESSION_EXIT_CODE=$?
cat /logs/verifier/regression_output.log
cp /tmp/r2e_regression_ctrf.json /logs/verifier/regression_ctrf.json 2>/dev/null || true
# -S keeps agent-planted sitecustomize.py/.pth files out of the grader.
python3 -S "$SCRIPT_DIR/verifier.py" \
  --log /logs/verifier/test_output.log \
  --f2p "$SCRIPT_DIR/f2p.json" --p2p "$SCRIPT_DIR/p2p.json" \
  --test-cmds 'pytest -v -n 0 tests/gateway/test_config.py' --exit-code "$TEST_EXIT_CODE" \
  --ctrf /logs/verifier/ctrf.json \
  --require-clean-command $DEGRADED_FLAG --regression "$SCRIPT_DIR/regression.json" --regression-log /logs/verifier/regression_output.log --regression-exit-code "$REGRESSION_EXIT_CODE" --regression-ctrf /logs/verifier/regression_ctrf.json \
  --out-dir /logs/verifier || \
  echo "0.0" > /logs/verifier/reward.txt
# reward.txt is the verdict, not this script's exit code.
exit 0
