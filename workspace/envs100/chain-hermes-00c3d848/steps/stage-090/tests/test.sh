#!/bin/bash
# Harbor step verifier. Placeholders are substituted by _pr_chain_steps.py
# via string.Template; every literal shell dollar is written as $ here.
#          toolchain PATH prefix (may be empty)
#   pytest -v -n 0 tests/test_hermes_state.py          the test command chain
#   pytest -v -n 0 tests/test_hermes_state.py  the same chain, single-quote-escaped for --test-cmds
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
  env PYTHONDONTWRITEBYTECODE=1 bash -c 'pytest -v -n 0 tests/test_hermes_state.py --ctrf /tmp/r2e_ctrf.json -p no:cacheprovider' \
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
  env PYTHONDONTWRITEBYTECODE=1 bash -c 'pytest -v -n 0 tests/agent/test_context_compressor.py tests/agent/test_model_metadata.py tests/agent/test_nous_rate_guard.py tests/agent/test_onboarding.py tests/agent/test_shell_hooks_consent.py tests/agent/test_title_generator.py tests/agent/test_unsupported_parameter_retry.py tests/cli/test_branch_command.py tests/cli/test_busy_input_mode_command.py tests/cli/test_cli_approval_ui.py tests/cli/test_cli_force_redraw.py tests/cli/test_cli_shutdown_memory_messages.py tests/cli/test_cli_terminal_response_sanitizer.py tests/cli/test_save_conversation_location.py tests/cron/test_cron_context_from.py tests/cron/test_jobs.py tests/cron/test_scheduler.py tests/gateway/test_agent_cache.py tests/gateway/test_busy_session_ack.py tests/gateway/test_compress_command.py tests/gateway/test_gateway_shutdown.py tests/gateway/test_keep_typing_timeout.py tests/gateway/test_matrix.py tests/gateway/test_media_download_retry.py tests/gateway/test_message_deduplicator.py tests/gateway/test_mirror.py tests/gateway/test_queue_consumption.py tests/gateway/test_reasoning_command.py tests/gateway/test_restart_drain.py tests/gateway/test_run_progress_interrupt.py tests/gateway/test_session_hygiene.py tests/gateway/test_session_list_allowed_sources.py tests/gateway/test_session_model_override_routing.py tests/gateway/test_session_model_reset.py tests/gateway/test_shutdown_cache_cleanup.py tests/gateway/test_shutdown_memory_provider_messages.py tests/gateway/test_slack.py tests/gateway/test_slack_mention.py tests/gateway/test_stream_consumer_fresh_final.py tests/gateway/test_telegram_group_gating.py tests/gateway/test_update_streaming.py tests/gateway/test_voice_command.py tests/hermes_cli/test_apply_model_switch_result_context.py tests/hermes_cli/test_backup.py tests/hermes_cli/test_commands.py tests/hermes_cli/test_custom_provider_model_switch.py tests/hermes_cli/test_doctor.py tests/hermes_cli/test_fallback_cmd.py tests/hermes_cli/test_model_catalog.py tests/hermes_cli/test_model_switch_context_display.py tests/hermes_cli/test_model_validation.py tests/hermes_cli/test_runtime_provider_resolution.py tests/hermes_cli/test_setup_ollama_cloud_force_refresh.py tests/hermes_cli/test_setup_reconfigure.py tests/hermes_cli/test_skills_hub.py tests/hermes_cli/test_tools_config.py tests/hermes_cli/test_tui_npm_install.py tests/honcho_plugin/test_client.py tests/honcho_plugin/test_pin_peer_name.py tests/plugins/memory/test_hindsight_provider.py tests/run_agent/test_background_review.py tests/run_agent/test_background_review_toolset_restriction.py tests/run_agent/test_deepseek_reasoning_content_echo.py tests/run_agent/test_review_prompt_class_first.py tests/run_agent/test_stream_interrupt_retry.py tests/skills/test_openclaw_migration.py tests/test_hermes_logging.py tests/test_hermes_state.py tests/test_model_tools.py tests/test_tui_gateway_server.py tests/tools/test_approval_plugin_hooks.py tests/tools/test_browser_hybrid_routing.py tests/tools/test_browser_ssrf_local.py tests/tools/test_checkpoint_manager.py tests/tools/test_cron_approval_mode.py tests/tools/test_delegate.py tests/tools/test_file_read_guards.py tests/tools/test_hardline_blocklist.py tests/tools/test_send_message_tool.py tests/tools/test_session_search.py tests/tools/test_shared_container_task_id.py tests/tools/test_skills_hub.py tests/tools/test_url_safety.py tests/tools/test_watch_patterns.py tests/tools/test_yolo_mode.py tests/tui_gateway/test_protocol.py tests/website/test_generate_skill_docs.py --ctrf /tmp/r2e_regression_ctrf.json -p no:cacheprovider' \
  > /logs/verifier/regression_output.log 2>&1
REGRESSION_EXIT_CODE=$?
cat /logs/verifier/regression_output.log
cp /tmp/r2e_regression_ctrf.json /logs/verifier/regression_ctrf.json 2>/dev/null || true
# -S keeps agent-planted sitecustomize.py/.pth files out of the grader.
python3 -S "$SCRIPT_DIR/verifier.py" \
  --log /logs/verifier/test_output.log \
  --f2p "$SCRIPT_DIR/f2p.json" --p2p "$SCRIPT_DIR/p2p.json" \
  --test-cmds 'pytest -v -n 0 tests/test_hermes_state.py' --exit-code "$TEST_EXIT_CODE" \
  --ctrf /logs/verifier/ctrf.json \
  --require-clean-command $DEGRADED_FLAG --regression "$SCRIPT_DIR/regression.json" --regression-log /logs/verifier/regression_output.log --regression-exit-code "$REGRESSION_EXIT_CODE" --regression-ctrf /logs/verifier/regression_ctrf.json \
  --out-dir /logs/verifier || \
  echo "0.0" > /logs/verifier/reward.txt
# reward.txt is the verdict, not this script's exit code.
exit 0
