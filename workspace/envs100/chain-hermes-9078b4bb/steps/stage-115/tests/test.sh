#!/bin/bash
# Harbor step verifier. Placeholders are substituted by _pr_chain_steps.py
# via string.Template; every literal shell dollar is written as $ here.
#          toolchain PATH prefix (may be empty)
#   pytest -v -n 0 tests/test_hermes_constants.py tests/tools/test_browser_hardening.py tests/tools/test_browser_homebrew_paths.py          the test command chain
#   pytest -v -n 0 tests/test_hermes_constants.py tests/tools/test_browser_hardening.py tests/tools/test_browser_homebrew_paths.py  the same chain, single-quote-escaped for --test-cmds
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
  env PYTHONDONTWRITEBYTECODE=1 bash -c 'pytest -v -n 0 tests/test_hermes_constants.py tests/tools/test_browser_hardening.py tests/tools/test_browser_homebrew_paths.py --ctrf /tmp/r2e_ctrf.json -p no:cacheprovider' \
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
  env PYTHONDONTWRITEBYTECODE=1 bash -c 'pytest -v -n 0 tests/acp/test_session.py tests/agent/test_anthropic_adapter.py tests/agent/test_auxiliary_client.py tests/agent/test_coding_context.py tests/agent/test_compression_count_warning_36908.py tests/agent/test_compression_progress.py tests/agent/test_compressor_tool_call_budget.py tests/agent/test_context_compressor.py tests/agent/test_learn_prompt.py tests/agent/test_memory_write_bridge.py tests/agent/test_oneshot.py tests/agent/test_prompt_builder.py tests/agent/test_redact.py tests/agent/test_usage_pricing.py tests/cli/test_cli_background_status_indicator.py tests/cli/test_cli_goal_interrupt.py tests/cli/test_cli_init.py tests/cli/test_worktree_sync_base.py tests/computer_use/test_cua_telemetry.py tests/cron/test_jobs.py tests/cron/test_scheduler.py tests/gateway/relay/test_relay_going_idle.py tests/gateway/relay/test_relay_passthrough.py tests/gateway/relay/test_relay_policy_send.py tests/gateway/relay/test_self_provision.py tests/gateway/test_13121_shutdown_inflight_transcript_flush.py tests/gateway/test_approval_prompt_redaction.py tests/gateway/test_async_delivery_capability.py tests/gateway/test_discord_component_auth.py tests/gateway/test_discord_double_dispatch.py tests/gateway/test_display_config.py tests/gateway/test_email.py tests/gateway/test_goal_verdict_send.py tests/gateway/test_kanban_auto_decompose_live.py tests/gateway/test_matrix.py tests/gateway/test_media_download_retry.py tests/gateway/test_model_command_expensive_confirm.py tests/gateway/test_platform_base.py tests/gateway/test_send_error_classification.py tests/gateway/test_session.py tests/gateway/test_session_split_brain_11016.py tests/gateway/test_session_store_prune.py tests/gateway/test_status.py tests/gateway/test_stream_consumer.py tests/gateway/test_telegram_closewait_limits_31599.py tests/gateway/test_telegram_format.py tests/gateway/test_telegram_prune_stale_topic_binding_31501.py tests/gateway/test_tui_approval_redaction.py tests/gateway/test_whatsapp_connect.py tests/gateway/test_whatsapp_to_jid.py tests/hermes_cli/test_active_sessions.py tests/hermes_cli/test_atomic_yaml_write.py tests/hermes_cli/test_backup.py tests/hermes_cli/test_banner.py tests/hermes_cli/test_config.py tests/hermes_cli/test_container_boot.py tests/hermes_cli/test_cron.py tests/hermes_cli/test_ctrlg_editor_submit.py tests/hermes_cli/test_dashboard_auth_ws_auth.py tests/hermes_cli/test_gateway.py tests/hermes_cli/test_gateway_windows.py tests/hermes_cli/test_goals.py tests/hermes_cli/test_inventory.py tests/hermes_cli/test_kanban_db.py tests/hermes_cli/test_kanban_dispatch_lock.py tests/hermes_cli/test_kanban_goal_mode.py tests/hermes_cli/test_kanban_init_lock_bounded.py tests/hermes_cli/test_kanban_lifecycle_hooks.py tests/hermes_cli/test_kanban_worker_terminal_cwd.py tests/hermes_cli/test_model_switch_custom_providers.py tests/hermes_cli/test_nous_auth_keepalive.py tests/hermes_cli/test_plugins.py tests/hermes_cli/test_profiles.py tests/hermes_cli/test_prompt_compose_command.py tests/hermes_cli/test_reasoning_full_command.py tests/hermes_cli/test_runtime_provider_resolution.py tests/hermes_cli/test_set_config_value.py tests/hermes_cli/test_slack_cli.py tests/hermes_cli/test_timestamps_command.py tests/hermes_cli/test_update_check.py tests/hermes_cli/test_update_concurrent_quarantine.py tests/hermes_cli/test_update_zip_atomic_replace.py tests/hermes_cli/test_web_server.py tests/plugins/test_hindsight_health_grace_timeout.py tests/plugins/test_hindsight_root_guard.py tests/plugins/test_kanban_dashboard_plugin.py tests/run_agent/test_413_compression.py tests/run_agent/test_background_review.py tests/run_agent/test_background_review_cost_controls.py tests/run_agent/test_codex_app_server_integration.py tests/run_agent/test_create_openai_client_proxy_env.py tests/run_agent/test_deepseek_reasoning_content_echo.py tests/run_agent/test_image_shrink_recovery.py tests/run_agent/test_provider_attribution_headers.py tests/run_agent/test_provider_parity.py tests/run_agent/test_run_agent.py tests/run_agent/test_tool_call_incremental_persistence.py tests/skills/test_cloudflare_temporary_deploy_skill.py tests/test_code_skew.py tests/test_delegate_cascade_49148.py tests/test_hermes_constants.py tests/test_model_tools.py tests/test_stale_utils_module_import.py tests/test_tui_gateway_server.py tests/test_web_server.py tests/tools/test_browser_orphan_reaper.py tests/tools/test_code_execution.py tests/tools/test_computer_use.py tests/tools/test_cronjob_tools.py tests/tools/test_file_read_guards.py tests/tools/test_file_tools_tilde_profile.py tests/tools/test_kanban_redaction.py tests/tools/test_local_env_blocklist.py tests/tools/test_notify_on_complete.py tests/tools/test_smart_approval_injection.py tests/tools/test_terminal_config_env_sync.py tests/tools/test_write_approval.py tests/tui_gateway/test_protocol.py --ctrf /tmp/r2e_regression_ctrf.json -p no:cacheprovider' \
  > /logs/verifier/regression_output.log 2>&1
REGRESSION_EXIT_CODE=$?
cat /logs/verifier/regression_output.log
cp /tmp/r2e_regression_ctrf.json /logs/verifier/regression_ctrf.json 2>/dev/null || true
# -S keeps agent-planted sitecustomize.py/.pth files out of the grader.
python3 -S "$SCRIPT_DIR/verifier.py" \
  --log /logs/verifier/test_output.log \
  --f2p "$SCRIPT_DIR/f2p.json" --p2p "$SCRIPT_DIR/p2p.json" \
  --test-cmds 'pytest -v -n 0 tests/test_hermes_constants.py tests/tools/test_browser_hardening.py tests/tools/test_browser_homebrew_paths.py' --exit-code "$TEST_EXIT_CODE" \
  --ctrf /logs/verifier/ctrf.json \
  --require-clean-command --regression "$SCRIPT_DIR/regression.json" --regression-log /logs/verifier/regression_output.log --regression-exit-code "$REGRESSION_EXIT_CODE" --regression-ctrf /logs/verifier/regression_ctrf.json \
  --out-dir /logs/verifier || \
  echo "0.0" > /logs/verifier/reward.txt
# reward.txt is the verdict, not this script's exit code.
exit 0
