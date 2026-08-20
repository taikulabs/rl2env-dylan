#!/bin/bash
# Harbor step verifier. Placeholders are substituted by _pr_chain_steps.py
# via string.Template; every literal shell dollar is written as $ here.
#          toolchain PATH prefix (may be empty)
#   pytest -v -n 0 tests/gateway/test_config.py tests/gateway/test_session.py          the test command chain
#   pytest -v -n 0 tests/gateway/test_config.py tests/gateway/test_session.py  the same chain, single-quote-escaped for --test-cmds
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
( pytest -v -n 0 tests/gateway/test_config.py tests/gateway/test_session.py ) > /logs/verifier/test_output.log 2>&1
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
( pytest -v -n 0 tests/agent/test_auxiliary_client.py tests/agent/test_context_compressor.py tests/agent/test_prompt_builder.py tests/agent/test_prompt_caching.py tests/agent/test_skill_commands.py tests/cron/test_scheduler.py tests/gateway/test_config.py tests/gateway/test_delivery.py tests/gateway/test_discord_free_response.py tests/gateway/test_discord_imports.py tests/gateway/test_discord_media_metadata.py tests/gateway/test_discord_send.py tests/gateway/test_discord_slash_commands.py tests/gateway/test_email.py tests/gateway/test_gateway_shutdown.py tests/gateway/test_homeassistant.py tests/gateway/test_honcho_lifecycle.py tests/gateway/test_interrupt_key_match.py tests/gateway/test_plan_command.py tests/gateway/test_platform_base.py tests/gateway/test_reasoning_command.py tests/gateway/test_resume_command.py tests/gateway/test_runner_fatal_adapter.py tests/gateway/test_send_image_file.py tests/gateway/test_session.py tests/gateway/test_session_env.py tests/gateway/test_slack.py tests/gateway/test_status.py tests/gateway/test_status_command.py tests/gateway/test_stt_config.py tests/gateway/test_telegram_conflict.py tests/gateway/test_telegram_documents.py tests/gateway/test_telegram_format.py tests/gateway/test_telegram_photo_interrupts.py tests/gateway/test_update_command.py tests/hermes_cli/test_chat_skills_flag.py tests/hermes_cli/test_cmd_update.py tests/hermes_cli/test_config.py tests/hermes_cli/test_doctor.py tests/hermes_cli/test_env_loader.py tests/hermes_cli/test_gateway.py tests/hermes_cli/test_gateway_linger.py tests/hermes_cli/test_gateway_runtime_health.py tests/hermes_cli/test_gateway_service.py tests/hermes_cli/test_model_validation.py tests/hermes_cli/test_placeholder_usage.py tests/hermes_cli/test_sessions_delete.py tests/hermes_cli/test_setup.py tests/hermes_cli/test_setup_model_provider.py tests/hermes_cli/test_setup_noninteractive.py tests/hermes_cli/test_setup_openclaw_migration.py tests/hermes_cli/test_setup_prompt_menus.py tests/hermes_cli/test_skills_hub.py tests/hermes_cli/test_skills_install_flags.py tests/hermes_cli/test_skin_engine.py tests/hermes_cli/test_status_model_provider.py tests/hermes_cli/test_tools_config.py tests/hermes_cli/test_update_autostash.py tests/hermes_cli/test_update_check.py tests/skills/test_google_oauth_setup.py tests/test_agent_loop.py tests/test_anthropic_adapter.py tests/test_anthropic_oauth_flow.py tests/test_anthropic_provider_persistence.py tests/test_api_key_providers.py tests/test_atomic_json_write.py tests/test_auxiliary_config_bridge.py tests/test_cli_approval_ui.py tests/test_cli_mcp_config_watch.py tests/test_cli_model_command.py tests/test_cli_new_session.py tests/test_cli_plan_command.py tests/test_cli_prefix_matching.py tests/test_cli_preloaded_skills.py tests/test_cli_provider_resolution.py tests/test_cli_skin_integration.py tests/test_codex_models.py tests/test_hermes_state.py tests/test_minisweagent_path.py tests/test_openai_client_lifecycle.py tests/test_provider_parity.py tests/test_quick_commands.py tests/test_run_agent.py tests/test_runtime_provider_resolution.py tests/test_tool_call_parsers.py tests/test_trajectory_compressor.py tests/test_worktree_security.py tests/tools/test_approval.py tests/tools/test_browser_cleanup.py tests/tools/test_checkpoint_manager.py tests/tools/test_cronjob_tools.py tests/tools/test_delegate.py tests/tools/test_docker_environment.py tests/tools/test_file_tools.py tests/tools/test_honcho_tools.py tests/tools/test_interrupt.py tests/tools/test_local_env_blocklist.py tests/tools/test_mcp_tool_issue_948.py tests/tools/test_memory_tool.py tests/tools/test_mixture_of_agents_tool.py tests/tools/test_patch_parser.py tests/tools/test_process_registry.py tests/tools/test_send_message_tool.py tests/tools/test_skills_guard.py tests/tools/test_skills_hub.py tests/tools/test_skills_hub_clawhub.py tests/tools/test_terminal_requirements.py tests/tools/test_terminal_tool_requirements.py tests/tools/test_tirith_security.py tests/tools/test_transcription.py tests/tools/test_transcription_tools.py ) > /logs/verifier/regression_output.log 2>&1 || true
cat /logs/verifier/regression_output.log
# -S keeps agent-planted sitecustomize.py/.pth files out of the grader.
python3 -S "$SCRIPT_DIR/verifier.py" \
  --log /logs/verifier/test_output.log \
  --f2p "$SCRIPT_DIR/f2p.json" --p2p "$SCRIPT_DIR/p2p.json" \
  --test-cmds 'pytest -v -n 0 tests/gateway/test_config.py tests/gateway/test_session.py' --exit-code "$TEST_EXIT_CODE" \
  --require-clean-command --regression "$SCRIPT_DIR/regression.json" --regression-log /logs/verifier/regression_output.log \
  --out-dir /logs/verifier || \
  echo "0.0" > /logs/verifier/reward.txt
# reward.txt is the verdict, not this script's exit code.
exit 0
