#!/bin/bash
# pr_arc single-task verifier. Placeholders substituted by pr_arc.py via
# string.Template ($ is a literal dollar):
#   pytest -v -n 0 tests/tools/test_browser_ssrf_local.py tests/tools/test_url_safety.py tests/plugins/memory/test_hindsight_provider.py tests/gateway/test_mirror.py tests/tools/test_send_message_tool.py tests/gateway/test_update_streaming.py tests/cli/test_save_conversation_location.py tests/gateway/test_session_list_allowed_sources.py tests/hermes_cli/test_session_browse.py tests/hermes_cli/test_setup_ollama_cloud_force_refresh.py          the graded test command chain
#   pytest -v -n 0 tests/tools/test_browser_ssrf_local.py tests/tools/test_url_safety.py tests/plugins/memory/test_hindsight_provider.py tests/gateway/test_mirror.py tests/tools/test_send_message_tool.py tests/gateway/test_update_streaming.py tests/cli/test_save_conversation_location.py tests/gateway/test_session_list_allowed_sources.py tests/hermes_cli/test_session_browse.py tests/hermes_cli/test_setup_ollama_cloud_force_refresh.py --ctrf /tmp/r2e_ctrf.json     the same commands with CTRF + no-cacheprovider flags
#   pytest -v -n 0 tests/tools/test_browser_ssrf_local.py tests/tools/test_url_safety.py tests/plugins/memory/test_hindsight_provider.py tests/gateway/test_mirror.py tests/tools/test_send_message_tool.py tests/gateway/test_update_streaming.py tests/cli/test_save_conversation_location.py tests/gateway/test_session_list_allowed_sources.py tests/hermes_cli/test_session_browse.py tests/hermes_cli/test_setup_ollama_cloud_force_refresh.py  the chain, single-quote-escaped for --test-cmds
set -uxo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd /workspace || exit 1
git config --global --add safe.directory /workspace
mkdir -p /logs/verifier
# Purge harness files the trusted bundle does not provide (planted conftest.py
# or pytest.ini can fabricate results), then restore the trusted copies.
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
# The graded run executes agent code, so it runs UNPRIVILEGED as nobody and
# the reward channel is locked to root first. The sweeps give the run read
# access to the toolchain and home, and write access to the workspace (tests
# legitimately mkdir log/scratch dirs there).
chmod 700 /logs/verifier
chmod -R a+rwX /root 2>/dev/null || true
chmod -R a+rX /opt/venv 2>/dev/null || true
chmod -R a+rwX /workspace 2>/dev/null || true
rm -f /tmp/r2e_ctrf.json
( setpriv --reuid nobody --regid nogroup --clear-groups --no-new-privs \
  env PYTHONDONTWRITEBYTECODE=1 bash -c 'pytest -v -n 0 tests/tools/test_browser_ssrf_local.py tests/tools/test_url_safety.py tests/plugins/memory/test_hindsight_provider.py tests/gateway/test_mirror.py tests/tools/test_send_message_tool.py tests/gateway/test_update_streaming.py tests/cli/test_save_conversation_location.py tests/gateway/test_session_list_allowed_sources.py tests/hermes_cli/test_session_browse.py tests/hermes_cli/test_setup_ollama_cloud_force_refresh.py --ctrf /tmp/r2e_ctrf.json' \
) > /logs/verifier/test_output.log 2>&1
TEST_EXIT_CODE=$?
cat /logs/verifier/test_output.log
cp /tmp/r2e_ctrf.json /logs/verifier/ctrf.json 2>/dev/null || true
# -S keeps agent-planted sitecustomize.py/.pth files out of the grader.
python3 -S "$SCRIPT_DIR/verifier.py" \
  --log /logs/verifier/test_output.log \
  --f2p "$SCRIPT_DIR/f2p.json" --p2p "$SCRIPT_DIR/p2p.json" \
  --test-cmds 'pytest -v -n 0 tests/tools/test_browser_ssrf_local.py tests/tools/test_url_safety.py tests/plugins/memory/test_hindsight_provider.py tests/gateway/test_mirror.py tests/tools/test_send_message_tool.py tests/gateway/test_update_streaming.py tests/cli/test_save_conversation_location.py tests/gateway/test_session_list_allowed_sources.py tests/hermes_cli/test_session_browse.py tests/hermes_cli/test_setup_ollama_cloud_force_refresh.py' --exit-code "$TEST_EXIT_CODE" \
  --ctrf /logs/verifier/ctrf.json \
  --require-clean-command --binary \
  --out-dir /logs/verifier || \
  echo "0.0" > /logs/verifier/reward.txt
# reward.txt is the verdict, not this script's exit code.
exit 0
