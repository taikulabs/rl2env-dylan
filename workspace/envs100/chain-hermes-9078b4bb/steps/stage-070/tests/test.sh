#!/bin/bash
# Harbor step verifier. Placeholders are substituted by _pr_chain_steps.py
# via string.Template; every literal shell dollar is written as $ here.
#          toolchain PATH prefix (may be empty)
#   pytest -v -n 0 tests/hermes_cli/test_inventory.py tests/hermes_cli/test_model_switch_custom_providers.py          the test command chain
#   pytest -v -n 0 tests/hermes_cli/test_inventory.py tests/hermes_cli/test_model_switch_custom_providers.py  the same chain, single-quote-escaped for --test-cmds
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
  env PYTHONDONTWRITEBYTECODE=1 bash -c 'pytest -v -n 0 tests/hermes_cli/test_inventory.py tests/hermes_cli/test_model_switch_custom_providers.py --ctrf /tmp/r2e_ctrf.json -p no:cacheprovider' \
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
  env PYTHONDONTWRITEBYTECODE=1 bash -c 'pytest -v -n 0 tests/acp/test_session.py tests/agent/test_anthropic_adapter.py tests/agent/test_auxiliary_client.py tests/agent/test_compression_count_warning_36908.py tests/agent/test_compression_progress.py tests/agent/test_compressor_tool_call_budget.py tests/agent/test_context_compressor.py tests/agent/test_redact.py tests/agent/test_usage_pricing.py tests/cli/test_cli_init.py tests/cli/test_worktree_sync_base.py tests/cron/test_jobs.py tests/cron/test_scheduler.py tests/gateway/relay/test_relay_passthrough.py tests/gateway/relay/test_self_provision.py tests/gateway/test_13121_shutdown_inflight_transcript_flush.py tests/gateway/test_approval_prompt_redaction.py tests/gateway/test_async_delivery_capability.py tests/gateway/test_email.py tests/gateway/test_kanban_auto_decompose_live.py tests/gateway/test_media_download_retry.py tests/gateway/test_model_command_expensive_confirm.py tests/gateway/test_platform_base.py tests/gateway/test_send_error_classification.py tests/gateway/test_session.py tests/gateway/test_status.py tests/gateway/test_stream_consumer.py tests/gateway/test_whatsapp_connect.py tests/gateway/test_whatsapp_to_jid.py tests/hermes_cli/test_backup.py tests/hermes_cli/test_banner.py tests/hermes_cli/test_config.py tests/hermes_cli/test_container_boot.py tests/hermes_cli/test_ctrlg_editor_submit.py tests/hermes_cli/test_dashboard_auth_ws_auth.py tests/hermes_cli/test_kanban_db.py tests/hermes_cli/test_kanban_dispatch_lock.py tests/hermes_cli/test_kanban_init_lock_bounded.py tests/hermes_cli/test_kanban_lifecycle_hooks.py tests/hermes_cli/test_kanban_worker_terminal_cwd.py tests/hermes_cli/test_nous_auth_keepalive.py tests/hermes_cli/test_plugins.py tests/hermes_cli/test_prompt_compose_command.py tests/hermes_cli/test_reasoning_full_command.py tests/hermes_cli/test_runtime_provider_resolution.py tests/hermes_cli/test_set_config_value.py tests/hermes_cli/test_timestamps_command.py tests/hermes_cli/test_update_check.py tests/hermes_cli/test_update_concurrent_quarantine.py tests/hermes_cli/test_update_zip_atomic_replace.py tests/plugins/test_hindsight_health_grace_timeout.py tests/plugins/test_hindsight_root_guard.py tests/plugins/test_kanban_dashboard_plugin.py tests/run_agent/test_413_compression.py tests/run_agent/test_background_review.py tests/run_agent/test_codex_app_server_integration.py tests/run_agent/test_create_openai_client_proxy_env.py tests/run_agent/test_deepseek_reasoning_content_echo.py tests/run_agent/test_provider_attribution_headers.py tests/run_agent/test_provider_parity.py tests/run_agent/test_run_agent.py tests/test_delegate_cascade_49148.py tests/test_hermes_constants.py tests/test_model_tools.py tests/test_tui_gateway_server.py tests/tools/test_browser_orphan_reaper.py tests/tools/test_code_execution.py tests/tools/test_file_read_guards.py tests/tools/test_kanban_redaction.py tests/tools/test_local_env_blocklist.py tests/tools/test_notify_on_complete.py tests/tools/test_smart_approval_injection.py tests/tools/test_terminal_config_env_sync.py --ctrf /tmp/r2e_regression_ctrf.json -p no:cacheprovider' \
  > /logs/verifier/regression_output.log 2>&1
REGRESSION_EXIT_CODE=$?
cat /logs/verifier/regression_output.log
cp /tmp/r2e_regression_ctrf.json /logs/verifier/regression_ctrf.json 2>/dev/null || true
# -S keeps agent-planted sitecustomize.py/.pth files out of the grader.
python3 -S "$SCRIPT_DIR/verifier.py" \
  --log /logs/verifier/test_output.log \
  --f2p "$SCRIPT_DIR/f2p.json" --p2p "$SCRIPT_DIR/p2p.json" \
  --test-cmds 'pytest -v -n 0 tests/hermes_cli/test_inventory.py tests/hermes_cli/test_model_switch_custom_providers.py' --exit-code "$TEST_EXIT_CODE" \
  --ctrf /logs/verifier/ctrf.json \
  --require-clean-command $DEGRADED_FLAG --regression "$SCRIPT_DIR/regression.json" --regression-log /logs/verifier/regression_output.log --regression-exit-code "$REGRESSION_EXIT_CODE" --regression-ctrf /logs/verifier/regression_ctrf.json \
  --out-dir /logs/verifier || \
  echo "0.0" > /logs/verifier/reward.txt
# reward.txt is the verdict, not this script's exit code.
exit 0
