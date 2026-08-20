**fix(streaming): surface dropped tool-call on mid-stream stall**

## Summary
Users no longer get a silent failure when a streaming model stalls mid tool-call — the dropped tool is now named in a user-visible warning appended to the assistant message.

## Root cause
When a stream dies after text was already delivered, the partial-stream recovery path at the end of `_interruptible_streaming_api_call` returns a stub with the recovered text and `tool_calls=None`, `finish_reason=stop`. That's correct for text-only stalls (retrying would duplicate the text), but when a tool call was in flight, the attempted action is lost with no indication — agent treats the turn as complete, session exits cleanly, nothing happened.

## Changes
- `run_agent.py`: streaming accumulator records each tool-call name into `result['partial_tool_names']` as soon as the name is known.
- `run_agent.py`: stub builder checks that list and, when non-empty, appends `⚠ Stream stalled mid tool-call (<names>); the action was not executed. Ask me to retry if you want to continue.` to `content`, and also fires it as a live stream delta so the user sees it *before* the turn closes, not just in the persisted transcript.
- `run_agent.py`: text-only partial streams keep the original bare-recovery behaviour (no warning noise for a scenario the previous design already handled correctly).
- `tests/run_agent/test_streaming.py`: two new regression tests — one asserts the warning fires + names the dropped tool + reaches the live delta callback, one asserts text-only partial streams are unchanged.

## Validation
| Scenario | Before | After |
|---|---|---|
| Stream dies mid tool-call, text already delivered | Silent exit code 0, no indication | Warning in content + live delta, user sees which tool was dropped |
| Text-only partial stream | Bare recovered text | Unchanged |
| `tests/run_agent/test_streaming.py` | 24 passed | 26 passed (2 new) |

---

## Reproduction methodology (for future re-verification)

### 1. Environment setup
```bash
# Isolated HERMES_HOME so prior state doesn't leak in
mkdir -p /tmp/hermes-minimax-eval && cp ~/.hermes/.env /tmp/hermes-minimax-eval/.env
cat > /tmp/hermes-minimax-eval/config.yaml <<'EOF'
_config_version: 5
display:
  streaming: true
agent:
  max_turns: 50
EOF
```

### 2. The trigger prompt
Substantive enough that MiniMax M2.7 emits leading commentary, starts a `write_file` tool call, and needs to generate a large JSON arguments blob — that's when the stall hits the 240 s stale-stream detector:
```bash
cat > /tmp/hermes-prompt.txt <<'EOF'
You have access to the hermes-agent repo at /home/teknium/.hermes/hermes-agent.
Audit how interrupts and subprocess cleanup work across ALL execution backends:

1. Read tools/environments/base.py, local.py, docker.py, ssh_env.py (if exists,
   else list what's there), modal_utils.py, and any daytona/singularity files.
2. For each backend identify: how _wait_for_process polls, how _kill_process
   works, what happens if the agent is interrupted mid-execution, what happens
   if the agent process crashes.
3. Check interrupt propagation to in-flight commands per backend.
4. Write a thorough markdown audit to /tmp/minimax-audit.md with one section
   per backend, including line-number references and concrete code excerpts.
5. At the end, list inconsistencies or potential bugs across backends.

Take your time, read actual code, don't speculate. I want real evidence.
EOF
```

### 3. Run the session (non-interactive, so `-q` captures the full lifecycle cleanly)
```bash
HERMES_HOME=/tmp/hermes-minimax-eval \
HERMES_DEBUG_INTERRUPT=1 \
PYTHONPATH=/home/teknium/.hermes/hermes-agent \
/home/teknium/.hermes/hermes-agent/venv/bin/python3 -m hermes_cli.main chat \
    --provider openrouter \
    --model minimax/minimax-m2.7 \
    --yolo \
    -q "$(cat /tmp/hermes-prompt.txt)" \
    2>&1 | tee /tmp/hermes-minimax-repro/session.log
```
(Note the slug form — `--provider openrouter --model minimax/minimax-m2.7`. Using `--model openrouter/minimax/minimax-m2.7` fails HTTP 400 "not a valid mo

…(truncated)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/run_agent/test_streaming.py`