#!/bin/bash
# Harbor step verifier. Placeholders are substituted by _pr_chain_steps.py
# via string.Template; every literal shell dollar is written as $ here.
#          toolchain PATH prefix (may be empty)
#   pytest -v -n 0 tests/gateway/test_telegram_pending_update_probe.py          the test command chain
#   pytest -v -n 0 tests/gateway/test_telegram_pending_update_probe.py  the same chain, single-quote-escaped for --test-cmds
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
( pytest -v -n 0 tests/gateway/test_telegram_pending_update_probe.py ) > /logs/verifier/test_output.log 2>&1
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
( pytest -v -n 0 tests/acp/test_approval_isolation.py tests/agent/lsp/test_reporter.py tests/agent/test_auxiliary_client.py tests/agent/test_coding_context.py tests/agent/test_compression_concurrent_fork.py tests/agent/test_context_breakdown.py tests/agent/test_context_compressor.py tests/agent/test_context_engine_host_contract.py tests/agent/test_credential_pool.py tests/agent/test_curator.py tests/agent/test_display.py tests/agent/test_error_classifier.py tests/agent/test_gemini_native_adapter.py tests/agent/test_intent_ack_continuation.py tests/agent/test_learning_mutations.py tests/agent/test_moa_switch_api_mode.py tests/agent/test_pet_engine.py tests/agent/test_redact.py tests/agent/test_shell_hooks.py tests/agent/test_turn_context.py tests/agent/test_verification_stop.py tests/agent/test_verify_hooks.py tests/cli/test_cli_approval_ui.py tests/gateway/test_10710_auto_reset_evicts_cached_agent.py tests/gateway/test_api_server.py tests/gateway/test_clean_shutdown_marker.py tests/gateway/test_config.py tests/gateway/test_config_env_bridge_authority.py tests/gateway/test_dead_targets.py tests/gateway/test_discord_edit_message_overflow.py tests/gateway/test_plaintext_approval_routing.py tests/gateway/test_platform_base.py tests/gateway/test_resume_command.py tests/gateway/test_run_progress_topics.py tests/gateway/test_session.py tests/gateway/test_session_store_runtime_stale_guard.py tests/gateway/test_slack_group_dm_scope_warning.py tests/gateway/test_slack_user_token_warning.py tests/gateway/test_slash_access_dispatch.py tests/gateway/test_stale_platform_lock_retryable.py tests/gateway/test_telegram_auth_check.py tests/gateway/test_telegram_pending_update_probe.py tests/gateway/test_typing_indicator_toggle.py tests/gateway/test_usage_command.py tests/gateway/test_wecom_callback.py tests/gateway/test_yuanbao_media_ssrf.py tests/hermes_cli/test_config.py tests/hermes_cli/test_container_boot.py tests/hermes_cli/test_cron.py tests/hermes_cli/test_gateway.py tests/hermes_cli/test_kanban_write_txn_busy_retry.py tests/hermes_cli/test_moa_config.py tests/hermes_cli/test_plugins.py tests/hermes_cli/test_plugins_cmd_enable_disable_nested.py tests/hermes_cli/test_profiles.py tests/hermes_cli/test_runtime_provider_resolution.py tests/hermes_cli/test_tools_config.py tests/hermes_cli/test_verify_console_scripts.py tests/hermes_cli/test_web_server.py tests/hermes_cli/test_web_server_pty_reconnect.py tests/plugins/dashboard_auth/test_self_hosted_provider.py tests/plugins/memory/test_mem0_v3.py tests/run_agent/test_agent_guardrails.py tests/run_agent/test_background_review_toolset_restriction.py tests/run_agent/test_message_sequence_repair.py tests/run_agent/test_moa_loop_mode.py tests/run_agent/test_streaming.py tests/test_fast_safe_load.py tests/test_hermes_state.py tests/test_install_diverged_update.py tests/test_output_cap_parsing.py tests/test_tui_gateway_server.py tests/test_windows_subprocess_no_window_flags.py tests/tools/test_browser_cdp_override.py tests/tools/test_browser_chromium_autoinstall.py tests/tools/test_browser_command_timeout_race.py tests/tools/test_browser_get_images_ssrf.py tests/tools/test_browser_open_timeout.py tests/tools/test_container_cwd_sanitize.py tests/tools/test_credential_pool_env_fallback.py tests/tools/test_daytona_environment.py tests/tools/test_delegate_summary_budget.py tests/tools/test_delegate_toolset_scope.py tests/tools/test_docker_cgroup_limits.py tests/tools/test_file_tools.py tests/tools/test_kanban_tools.py tests/tools/test_memory_tool.py tests/tools/test_modal_sandbox_fixes.py tests/tools/test_process_registry.py tests/tools/test_skills_hub.py tests/tools/test_vision_tools.py tests/tools/test_web_extract_robustness.py tests/tools/test_web_tools_truncate.py tests/tui_gateway/test_mcp_late_refresh_thread_owner.py tests/tui_gateway/test_model_switch_marker_role.py ) > /logs/verifier/regression_output.log 2>&1 || true
cat /logs/verifier/regression_output.log
# -S keeps agent-planted sitecustomize.py/.pth files out of the grader.
python3 -S "$SCRIPT_DIR/verifier.py" \
  --log /logs/verifier/test_output.log \
  --f2p "$SCRIPT_DIR/f2p.json" --p2p "$SCRIPT_DIR/p2p.json" \
  --test-cmds 'pytest -v -n 0 tests/gateway/test_telegram_pending_update_probe.py' --exit-code "$TEST_EXIT_CODE" \
  --require-clean-command --regression "$SCRIPT_DIR/regression.json" --regression-log /logs/verifier/regression_output.log \
  --out-dir /logs/verifier || \
  echo "0.0" > /logs/verifier/reward.txt
# reward.txt is the verdict, not this script's exit code.
exit 0
