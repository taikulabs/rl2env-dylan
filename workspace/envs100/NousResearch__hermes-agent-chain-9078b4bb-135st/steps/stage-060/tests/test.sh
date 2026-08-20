#!/bin/bash
# Harbor step verifier. Placeholders are substituted by _pr_chain_steps.py
# via string.Template; every literal shell dollar is written as $ here.
#          toolchain PATH prefix (may be empty)
#   pytest -v -n 0 tests/agent/test_anthropic_adapter.py          the test command chain
#   pytest -v -n 0 tests/agent/test_anthropic_adapter.py  the same chain, single-quote-escaped for --test-cmds
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
( pytest -v -n 0 tests/agent/test_anthropic_adapter.py ) > /logs/verifier/test_output.log 2>&1
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
( pytest -v -n 0 tests/acp/test_session.py tests/agent/test_auxiliary_client.py tests/agent/test_compression_count_warning_36908.py tests/agent/test_context_compressor.py tests/agent/test_redact.py tests/agent/test_usage_pricing.py tests/cli/test_cli_init.py tests/cli/test_worktree_sync_base.py tests/cron/test_jobs.py tests/gateway/relay/test_relay_passthrough.py tests/gateway/test_13121_shutdown_inflight_transcript_flush.py tests/gateway/test_async_delivery_capability.py tests/gateway/test_email.py tests/gateway/test_kanban_auto_decompose_live.py tests/gateway/test_media_download_retry.py tests/gateway/test_model_command_expensive_confirm.py tests/gateway/test_platform_base.py tests/gateway/test_send_error_classification.py tests/gateway/test_session.py tests/gateway/test_status.py tests/gateway/test_stream_consumer.py tests/gateway/test_whatsapp_connect.py tests/gateway/test_whatsapp_to_jid.py tests/hermes_cli/test_backup.py tests/hermes_cli/test_banner.py tests/hermes_cli/test_config.py tests/hermes_cli/test_container_boot.py tests/hermes_cli/test_ctrlg_editor_submit.py tests/hermes_cli/test_dashboard_auth_ws_auth.py tests/hermes_cli/test_kanban_db.py tests/hermes_cli/test_kanban_dispatch_lock.py tests/hermes_cli/test_kanban_init_lock_bounded.py tests/hermes_cli/test_kanban_lifecycle_hooks.py tests/hermes_cli/test_kanban_worker_terminal_cwd.py tests/hermes_cli/test_nous_auth_keepalive.py tests/hermes_cli/test_plugins.py tests/hermes_cli/test_prompt_compose_command.py tests/hermes_cli/test_reasoning_full_command.py tests/hermes_cli/test_runtime_provider_resolution.py tests/hermes_cli/test_set_config_value.py tests/hermes_cli/test_timestamps_command.py tests/hermes_cli/test_update_concurrent_quarantine.py tests/hermes_cli/test_update_zip_atomic_replace.py tests/plugins/test_hindsight_health_grace_timeout.py tests/plugins/test_hindsight_root_guard.py tests/plugins/test_kanban_dashboard_plugin.py tests/run_agent/test_413_compression.py tests/run_agent/test_background_review.py tests/run_agent/test_codex_app_server_integration.py tests/run_agent/test_create_openai_client_proxy_env.py tests/run_agent/test_deepseek_reasoning_content_echo.py tests/run_agent/test_provider_attribution_headers.py tests/run_agent/test_provider_parity.py tests/run_agent/test_run_agent.py tests/test_delegate_cascade_49148.py tests/test_hermes_constants.py tests/test_model_tools.py tests/test_tui_gateway_server.py tests/tools/test_browser_orphan_reaper.py tests/tools/test_code_execution.py tests/tools/test_file_read_guards.py tests/tools/test_kanban_redaction.py tests/tools/test_local_env_blocklist.py tests/tools/test_notify_on_complete.py tests/tools/test_smart_approval_injection.py tests/tools/test_terminal_config_env_sync.py ) > /logs/verifier/regression_output.log 2>&1 || true
cat /logs/verifier/regression_output.log
# -S keeps agent-planted sitecustomize.py/.pth files out of the grader.
python3 -S "$SCRIPT_DIR/verifier.py" \
  --log /logs/verifier/test_output.log \
  --f2p "$SCRIPT_DIR/f2p.json" --p2p "$SCRIPT_DIR/p2p.json" \
  --test-cmds 'pytest -v -n 0 tests/agent/test_anthropic_adapter.py' --exit-code "$TEST_EXIT_CODE" \
  --require-clean-command --regression "$SCRIPT_DIR/regression.json" --regression-log /logs/verifier/regression_output.log \
  --out-dir /logs/verifier || \
  echo "0.0" > /logs/verifier/reward.txt
# reward.txt is the verdict, not this script's exit code.
exit 0
