**fix(agent): propagate ContextVars to concurrent tool worker threads (salvage #16660)**

Salvages the core fix from #16660 by @banditburai (commit authored by @firefly). The original PR had scope contamination — a `tests/eval_018/` directory containing eval-oracle test files for a different project ("talaria") that fail 5/5 on hermes main (check for a non-existent `cli.CliError` class, a rename from `ContextCompressor`→`ContextCompactor` that never happened here, `talaria.tools._anchor_state` imports, a wrong `generate_title` timeout default, etc.). Those were dropped from this salvage.

## The real fix (4 LOC in run_agent.py)

`_execute_tool_calls_concurrent` submits tools via `executor.submit(_run_tool, ...)` without `copy_context().run`, so worker threads run with a fresh context — `tools.approval._approval_session_key` (set by gateway adapters before `agent.run`) is invisible. Workers fall through `get_current_session_key()`'s resolution order to the `os.environ` fallback (which every agent step overwrites), silently collapsing per-session dispatch to whichever session stepped most recently.

Fix: snapshot the caller's context and submit `ctx.run(_run_tool, …)`. Mirrors `asyncio.to_thread` semantics. The existing threading.local callback propagation at `run_agent.py:~8796` (from  / GHSA-qg5c-hvr5-hjgr) is preserved — that one handles a different propagation surface (approval/sudo callbacks) that ContextVars cannot carry across thread boundaries.

## Real-world repro

Via @syahidfrd on : two concurrent Slack sessions (channels A and B), session A's agent fired a dangerous-command approval for a recursive delete → approval card was delivered to **channel B** — the user there saw an approval prompt for a command they had no context for, while session A's thread blocked waiting for a response that would never come. Any user in B could click "Allow Once" without understanding what they were authorizing.

## Regression suite

`tests/run_agent/test_tool_executor_contextvar_propagation.py` — 5 guards, following the `contextvar-run-in-executor-bridge` skill's two-test pattern plus a source-level guard for the real call site:

1. **Contract documentation** — `executor.submit(fn)` without `copy_context` does NOT propagate ContextVars. If this ever flips, the fix becomes redundant.
2. **Contract validation** — `copy_context().run(fn)` does propagate. Positive baseline.
3. **End-to-end** — set the real `_approval_session_key` in a caller, verify the worker thread observes it via `get_current_session_key()`.
4. **Source-level guard** — AST-parses `run_agent.py` and asserts the `executor.submit` call site for `_run_tool` is invoked with `ctx.run` as its first arg. **This is the primary regression guard.** Behavioral tests 1-3 + 5 exercise the *pattern* but not the *real call site* — they keep passing even if someone reverts the wrapper in `run_agent.py`. Test 4 fails with a concrete diagnostic:

    ```
    AssertionError: run_agent.py contains `executor.submit(_run_tool, ...)`
    without a `ctx.run` wrapper. This is the  shape: worker
    threads will read a fresh ContextVar and approval-session routing
    collapses to the os.environ fallback.
    ```

5. **Concurrent-caller isolation** — two callers each set a different session key; each worker must see its own caller's key.

## Regression guard validation

Planted the pre-fix shape: reverted `run_agent.py` to `origin/main` → guard #4 fails with the diagnostic above ✓. Restored the fix → 5/5 pass ✓.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/run_agent/test_tool_executor_contextvar_propagation.py`