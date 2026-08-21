#!/bin/bash
# Harbor step verifier. Placeholders are substituted by _pr_chain_steps.py
# via string.Template; every literal shell dollar is written as $ here.
#          toolchain PATH prefix (may be empty)
#   pytest -v -n 0 tests/gateway/test_cancel_background_drain.py          the test command chain
#   pytest -v -n 0 tests/gateway/test_cancel_background_drain.py  the same chain, single-quote-escaped for --test-cmds
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
  env PYTHONDONTWRITEBYTECODE=1 bash -c 'pytest -v -n 0 tests/gateway/test_cancel_background_drain.py --ctrf /tmp/r2e_ctrf.json -p no:cacheprovider' \
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
  env PYTHONDONTWRITEBYTECODE=1 bash -c 'pytest -v -n 0 tests/agent/test_anthropic_adapter.py tests/agent/test_auxiliary_client.py tests/agent/test_auxiliary_main_first.py tests/agent/test_gemini_cloudcode.py tests/agent/test_insights.py tests/agent/test_nous_rate_guard.py tests/agent/test_proxy_and_url_validation.py tests/agent/test_redact.py tests/agent/test_vision_resolved_args.py tests/cli/test_cli_approval_ui.py tests/cli/test_cli_status_bar.py tests/cli/test_cli_status_command.py tests/cli/test_gquota_command.py tests/cli/test_quick_commands.py tests/cli/test_resume_display.py tests/cli/test_surrogate_sanitization.py tests/gateway/test_agent_cache.py tests/gateway/test_background_command.py tests/gateway/test_background_process_notifications.py tests/gateway/test_command_bypass_active_session.py tests/gateway/test_compress_command.py tests/gateway/test_config.py tests/gateway/test_dingtalk.py tests/gateway/test_discord_attachment_download.py tests/gateway/test_discord_send.py tests/gateway/test_discord_slash_commands.py tests/gateway/test_feishu.py tests/gateway/test_flush_memory_stale_guard.py tests/gateway/test_matrix.py tests/gateway/test_matrix_mention.py tests/gateway/test_pending_drain_race.py tests/gateway/test_restart_redelivery_dedup.py tests/gateway/test_restart_resume_pending.py tests/gateway/test_safe_adapter_disconnect.py tests/gateway/test_session_env.py tests/gateway/test_session_hygiene.py tests/gateway/test_session_race_guard.py tests/gateway/test_session_state_cleanup.py tests/gateway/test_session_store_prune.py tests/gateway/test_signal.py tests/gateway/test_slack.py tests/gateway/test_status_command.py tests/gateway/test_steer_command.py tests/gateway/test_stream_consumer.py tests/gateway/test_telegram_approval_buttons.py tests/gateway/test_telegram_format.py tests/gateway/test_telegram_thread_fallback.py tests/gateway/test_text_batching.py tests/hermes_cli/test_auth_commands.py tests/hermes_cli/test_auth_nous_provider.py tests/hermes_cli/test_aux_config.py tests/hermes_cli/test_config.py tests/hermes_cli/test_config_env_refs.py tests/hermes_cli/test_debug.py tests/hermes_cli/test_deprecated_cwd_warning.py tests/hermes_cli/test_gateway.py tests/hermes_cli/test_model_normalize.py tests/hermes_cli/test_model_switch_copilot_api_mode.py tests/hermes_cli/test_model_switch_opencode_anthropic.py tests/hermes_cli/test_ollama_cloud_provider.py tests/hermes_cli/test_plugins.py tests/hermes_cli/test_skin_engine.py tests/hermes_cli/test_tools_config.py tests/hermes_cli/test_update_gateway_restart.py tests/hermes_cli/test_update_hangup_protection.py tests/honcho_plugin/test_session.py tests/run_agent/test_memory_provider_init.py tests/run_agent/test_provider_parity.py tests/run_agent/test_steer.py tests/run_agent/test_streaming.py tests/skills/test_google_oauth_setup.py tests/skills/test_google_workspace_api.py tests/test_mini_swe_runner.py tests/test_project_metadata.py tests/test_trajectory_compressor.py tests/test_trajectory_compressor_async.py tests/test_tui_gateway_server.py tests/tools/test_accretion_caps.py tests/tools/test_approval.py tests/tools/test_approval_heartbeat.py tests/tools/test_browser_cdp_override.py tests/tools/test_browser_cdp_tool.py tests/tools/test_browser_cloud_fallback.py tests/tools/test_browser_orphan_reaper.py tests/tools/test_checkpoint_manager.py tests/tools/test_code_execution_modes.py tests/tools/test_cron_approval_mode.py tests/tools/test_file_ops_cwd_tracking.py tests/tools/test_file_sync_back.py tests/tools/test_image_generation.py tests/tools/test_send_message_tool.py tests/tools/test_skills_sync.py tests/tools/test_terminal_tool.py tests/tools/test_tts_gemini.py tests/tui_gateway/test_protocol.py --ctrf /tmp/r2e_regression_ctrf.json -p no:cacheprovider' \
  > /logs/verifier/regression_output.log 2>&1
REGRESSION_EXIT_CODE=$?
cat /logs/verifier/regression_output.log
cp /tmp/r2e_regression_ctrf.json /logs/verifier/regression_ctrf.json 2>/dev/null || true
# -S keeps agent-planted sitecustomize.py/.pth files out of the grader.
python3 -S "$SCRIPT_DIR/verifier.py" \
  --log /logs/verifier/test_output.log \
  --f2p "$SCRIPT_DIR/f2p.json" --p2p "$SCRIPT_DIR/p2p.json" \
  --test-cmds 'pytest -v -n 0 tests/gateway/test_cancel_background_drain.py' --exit-code "$TEST_EXIT_CODE" \
  --ctrf /logs/verifier/ctrf.json \
  --require-clean-command --regression "$SCRIPT_DIR/regression.json" --regression-log /logs/verifier/regression_output.log --regression-exit-code "$REGRESSION_EXIT_CODE" --regression-ctrf /logs/verifier/regression_ctrf.json \
  --out-dir /logs/verifier || \
  echo "0.0" > /logs/verifier/reward.txt
# reward.txt is the verdict, not this script's exit code.
exit 0
