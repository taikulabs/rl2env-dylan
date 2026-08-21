#!/bin/bash
# Harbor step verifier. Placeholders are substituted by _pr_chain_steps.py
# via string.Template; every literal shell dollar is written as $ here.
#          toolchain PATH prefix (may be empty)
#   pytest -v -n 0 tests/agent/test_context_compressor.py          the test command chain
#   pytest -v -n 0 tests/agent/test_context_compressor.py  the same chain, single-quote-escaped for --test-cmds
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
  env PYTHONDONTWRITEBYTECODE=1 bash -c 'pytest -v -n 0 tests/agent/test_context_compressor.py --ctrf /tmp/r2e_ctrf.json -p no:cacheprovider' \
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
  env PYTHONDONTWRITEBYTECODE=1 bash -c 'pytest -v -n 0 tests/acp/test_session.py tests/agent/test_auxiliary_client.py tests/agent/test_context_compressor.py tests/agent/test_model_metadata.py tests/agent/test_models_dev.py tests/agent/test_prompt_builder.py tests/agent/test_prompt_caching.py tests/agent/test_redact.py tests/agent/test_skill_commands.py tests/agent/test_title_generator.py tests/agent/test_usage_pricing.py tests/cron/test_jobs.py tests/cron/test_scheduler.py tests/gateway/test_agent_cache.py tests/gateway/test_api_server.py tests/gateway/test_api_server_jobs.py tests/gateway/test_approve_deny_commands.py tests/gateway/test_config.py tests/gateway/test_dingtalk.py tests/gateway/test_discord_document_handling.py tests/gateway/test_discord_slash_commands.py tests/gateway/test_flush_memory_stale_guard.py tests/gateway/test_mattermost.py tests/gateway/test_platform_reconnect.py tests/gateway/test_runner_fatal_adapter.py tests/gateway/test_send_image_file.py tests/gateway/test_session.py tests/gateway/test_session_race_guard.py tests/gateway/test_session_reset_notify.py tests/gateway/test_sms.py tests/gateway/test_status.py tests/gateway/test_telegram_conflict.py tests/gateway/test_telegram_documents.py tests/gateway/test_telegram_format.py tests/gateway/test_telegram_text_batching.py tests/gateway/test_unauthorized_dm_behavior.py tests/gateway/test_voice_command.py tests/gateway/test_whatsapp_connect.py tests/hermes_cli/test_banner.py tests/hermes_cli/test_banner_skills.py tests/hermes_cli/test_gateway.py tests/hermes_cli/test_mcp_tools_config.py tests/hermes_cli/test_model_validation.py tests/hermes_cli/test_setup.py tests/hermes_cli/test_setup_model_provider.py tests/hermes_cli/test_tools_config.py tests/hermes_cli/test_update_autostash.py tests/honcho_integration/test_client.py tests/test_agent_guardrails.py tests/test_anthropic_adapter.py tests/test_api_key_providers.py tests/test_auxiliary_config_bridge.py tests/test_cli_extension_hooks.py tests/test_cli_provider_resolution.py tests/test_compression_boundary.py tests/test_config_env_expansion.py tests/test_context_pressure.py tests/test_context_references.py tests/test_hermes_state.py tests/test_model_metadata_local_ctx.py tests/test_model_tools_async_bridge.py tests/test_plugins.py tests/test_plugins_cmd.py tests/test_run_agent.py tests/test_run_agent_codex_responses.py tests/test_runtime_provider_resolution.py tests/test_sql_injection.py tests/tools/test_approval.py tests/tools/test_browser_homebrew_paths.py tests/tools/test_daytona_environment.py tests/tools/test_docker_environment.py tests/tools/test_env_passthrough.py tests/tools/test_local_env_blocklist.py tests/tools/test_mcp_probe.py tests/tools/test_process_registry.py tests/tools/test_read_loop_detection.py tests/tools/test_send_message_tool.py tests/tools/test_session_search.py tests/tools/test_skill_env_passthrough.py tests/tools/test_skills_guard.py tests/tools/test_skills_tool.py tests/tools/test_terminal_disk_usage.py tests/tools/test_transcription.py tests/tools/test_transcription_tools.py tests/tools/test_url_safety.py tests/tools/test_vision_tools.py tests/tools/test_web_tools_config.py tests/tools/test_website_policy.py --ctrf /tmp/r2e_regression_ctrf.json -p no:cacheprovider' \
  > /logs/verifier/regression_output.log 2>&1
REGRESSION_EXIT_CODE=$?
cat /logs/verifier/regression_output.log
cp /tmp/r2e_regression_ctrf.json /logs/verifier/regression_ctrf.json 2>/dev/null || true
# -S keeps agent-planted sitecustomize.py/.pth files out of the grader.
python3 -S "$SCRIPT_DIR/verifier.py" \
  --log /logs/verifier/test_output.log \
  --f2p "$SCRIPT_DIR/f2p.json" --p2p "$SCRIPT_DIR/p2p.json" \
  --test-cmds 'pytest -v -n 0 tests/agent/test_context_compressor.py' --exit-code "$TEST_EXIT_CODE" \
  --ctrf /logs/verifier/ctrf.json \
  --require-clean-command --regression "$SCRIPT_DIR/regression.json" --regression-log /logs/verifier/regression_output.log --regression-exit-code "$REGRESSION_EXIT_CODE" --regression-ctrf /logs/verifier/regression_ctrf.json \
  --out-dir /logs/verifier || \
  echo "0.0" > /logs/verifier/reward.txt
# reward.txt is the verdict, not this script's exit code.
exit 0
