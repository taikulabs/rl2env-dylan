#!/bin/bash
# Harbor step verifier. Placeholders are substituted by _pr_chain_steps.py
# via string.Template; every literal shell dollar is written as $ here.
#          toolchain PATH prefix (may be empty)
#   pytest -v -n 0 tests/agent/test_models_dev.py tests/tools/test_vision_tools.py          the test command chain
#   pytest -v -n 0 tests/agent/test_models_dev.py tests/tools/test_vision_tools.py  the same chain, single-quote-escaped for --test-cmds
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
  env PYTHONDONTWRITEBYTECODE=1 bash -c 'pytest -v -n 0 tests/agent/test_models_dev.py tests/tools/test_vision_tools.py --ctrf /tmp/r2e_ctrf.json -p no:cacheprovider' \
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
  env PYTHONDONTWRITEBYTECODE=1 bash -c 'pytest -v -n 0 tests/acp/test_server.py tests/agent/test_anthropic_adapter.py tests/agent/test_auxiliary_client.py tests/agent/test_auxiliary_named_custom_providers.py tests/agent/test_context_references.py tests/agent/test_credential_pool.py tests/agent/test_error_classifier.py tests/agent/test_minimax_auxiliary_url.py tests/agent/test_minimax_provider.py tests/agent/test_model_metadata.py tests/agent/test_rate_limit_tracker.py tests/agent/test_subdirectory_hints.py tests/cli/test_cli_approval_ui.py tests/cli/test_cli_browser_connect.py tests/cli/test_fast_command.py tests/cli/test_manual_compress.py tests/cli/test_stream_delta_think_tag.py tests/cron/test_jobs.py tests/cron/test_scheduler.py tests/environments/benchmarks/test_terminalbench2_env_security.py tests/gateway/test_api_server.py tests/gateway/test_bluebubbles.py tests/gateway/test_compress_command.py tests/gateway/test_discord_document_handling.py tests/gateway/test_discord_reply_mode.py tests/gateway/test_feishu_approval_buttons.py tests/gateway/test_matrix.py tests/gateway/test_matrix_mention.py tests/gateway/test_media_download_retry.py tests/gateway/test_model_switch_persistence.py tests/gateway/test_platform_base.py tests/gateway/test_resume_command.py tests/gateway/test_runner_startup_failures.py tests/gateway/test_session_boundary_hooks.py tests/gateway/test_session_dm_thread_seeding.py tests/gateway/test_session_env.py tests/gateway/test_session_model_override_routing.py tests/gateway/test_signal.py tests/gateway/test_slack.py tests/gateway/test_status.py tests/gateway/test_stream_consumer.py tests/gateway/test_telegram_reactions.py tests/gateway/test_usage_command.py tests/gateway/test_yolo_command.py tests/hermes_cli/test_api_key_providers.py tests/hermes_cli/test_auth_nous_provider.py tests/hermes_cli/test_banner_git_state.py tests/hermes_cli/test_commands.py tests/hermes_cli/test_doctor.py tests/hermes_cli/test_gateway.py tests/hermes_cli/test_gateway_wsl.py tests/hermes_cli/test_model_switch_variant_tags.py tests/hermes_cli/test_model_validation.py tests/hermes_cli/test_models.py tests/hermes_cli/test_overlay_slug_resolution.py tests/hermes_cli/test_runtime_provider_resolution.py tests/hermes_cli/test_setup_openclaw_migration.py tests/hermes_cli/test_tools_config.py tests/hermes_cli/test_update_autostash.py tests/honcho_plugin/test_client.py tests/honcho_plugin/test_session.py tests/plugins/memory/test_hindsight_provider.py tests/run_agent/test_413_compression.py tests/run_agent/test_context_pressure.py tests/run_agent/test_flush_memories_codex.py tests/run_agent/test_primary_runtime_restore.py tests/run_agent/test_provider_parity.py tests/run_agent/test_run_agent.py tests/run_agent/test_run_agent_codex_responses.py tests/run_agent/test_unicode_ascii_codec.py tests/skills/test_openclaw_migration.py tests/test_cli_skin_integration.py tests/test_ctx_halving_fix.py tests/test_hermes_logging.py tests/test_hermes_state.py tests/test_ollama_num_ctx.py tests/test_project_metadata.py tests/test_retry_utils.py tests/test_subprocess_home_isolation.py tests/tools/test_approval.py tests/tools/test_browser_camofox_persistence.py tests/tools/test_browser_cleanup.py tests/tools/test_browser_hardening.py tests/tools/test_browser_homebrew_paths.py tests/tools/test_clipboard.py tests/tools/test_delegate.py tests/tools/test_mcp_structured_content.py tests/tools/test_notify_on_complete.py tests/tools/test_process_registry.py tests/tools/test_send_message_tool.py tests/tools/test_skills_sync.py tests/tools/test_terminal_foreground_timeout_cap.py tests/tools/test_terminal_none_command_guard.py tests/tools/test_terminal_tool.py tests/tools/test_tool_result_storage.py tests/tools/test_transcription_tools.py tests/tools/test_tts_mistral.py tests/tools/test_watch_patterns.py tests/tools/test_yolo_mode.py --ctrf /tmp/r2e_regression_ctrf.json -p no:cacheprovider' \
  > /logs/verifier/regression_output.log 2>&1
REGRESSION_EXIT_CODE=$?
cat /logs/verifier/regression_output.log
cp /tmp/r2e_regression_ctrf.json /logs/verifier/regression_ctrf.json 2>/dev/null || true
# -S keeps agent-planted sitecustomize.py/.pth files out of the grader.
python3 -S "$SCRIPT_DIR/verifier.py" \
  --log /logs/verifier/test_output.log \
  --f2p "$SCRIPT_DIR/f2p.json" --p2p "$SCRIPT_DIR/p2p.json" \
  --test-cmds 'pytest -v -n 0 tests/agent/test_models_dev.py tests/tools/test_vision_tools.py' --exit-code "$TEST_EXIT_CODE" \
  --ctrf /logs/verifier/ctrf.json \
  --require-clean-command $DEGRADED_FLAG --regression "$SCRIPT_DIR/regression.json" --regression-log /logs/verifier/regression_output.log --regression-exit-code "$REGRESSION_EXIT_CODE" --regression-ctrf /logs/verifier/regression_ctrf.json \
  --out-dir /logs/verifier || \
  echo "0.0" > /logs/verifier/reward.txt
# reward.txt is the verdict, not this script's exit code.
exit 0
