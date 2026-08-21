"""In-container verifier for pr_runtime tasks (graded F2P/P2P reward).

This module is the **standalone verifier** that runs inside the task's
Docker container, NOT a helper used at generation time. It is read as
source at generation time, base64-encoded, and embedded into
``tests/test.sh``. At run time the container decodes it back to a file
and invokes it after the test suite has run.

Why a graded reward instead of binary pass/fail
------------------------------------------------
SWE-bench resolution is binary: a patch "resolves" the issue iff ALL
FAIL_TO_PASS tests pass AND ALL PASS_TO_PASS tests still pass. That's
the right signal for an eval leaderboard, but a terrible gradient for
RL training — an agent that fixes 4 of 5 failing tests scores the same
0.0 as one that fixes nothing.

So this verifier emits BOTH:
  * /logs/verifier/reward.txt  — the GRADED scalar (training signal,
        which Harbor reads):  reward = f2p_rate * p2p_factor
  * /logs/verifier/reward-details.json — carries the strict SWE-bench
        ``resolved`` bool (eval signal) PLUS the full breakdown.

Refs: SWE-bench (F2P/P2P semantics), SWE-RL / SWE-Gym (dense reward for
RL), UTBoost (weak-test coverage lets wrong patches pass — hence we
record p2p_count so consumers can judge regression-guard strength).

Scoring
-------
Given the baked FAIL_TO_PASS / PASS_TO_PASS test-name lists (computed by
the generation-time two-stage validation) and the agent-run test log:

  f2p_rate   = (# F2P tests now PASSED) / (# F2P tests)
  p2p_rate   = (# P2P tests still PASSED) / (# P2P tests)   [1.0 if no P2P]
  p2p_factor = p2p_rate          # regressions scale the reward down
  reward     = f2p_rate * p2p_factor
  resolved   = (all F2P pass) AND (all P2P pass)            # strict SWE-bench

Oracle invariant: the gold patch flips every F2P and keeps every P2P,
so f2p_rate=1.0, p2p_rate=1.0 -> reward=1.0 and resolved=True. This is
what the T3 oracle gate (reward == 1.0) relies on.

Graceful degradation: if the log can't be parsed into per-test
statuses (unrecognized runner output), fall back to the exit-code
reward (1.0 if the suite exited 0, else 0.0) and stamp
``parse_status="fallback_exitcode"`` — never crash, never silently
zero out a real fix.

Pure stdlib — uses only ``argparse``, ``json``, ``os``, ``re``, ``sys``.
The 4 per-runner parsers are condensed ports of
``repo2rlenv.log_parsers.*`` kept in lockstep via the unit tests under
``tests/test_pr_runtime_verifier.py``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

# Canonical statuses. (Plain strings — no typing.Literal so the baked
# module stays import-light when decoded standalone in the container.)
PASSED = "PASSED"
FAILED = "FAILED"
SKIPPED = "SKIPPED"
ERROR = "ERROR"

# ---------------------------------------------------------------------------
# Per-runner log parsers (condensed ports of repo2rlenv.log_parsers.*)
# ---------------------------------------------------------------------------

_PYTEST_STATUSES = (PASSED, FAILED, SKIPPED, ERROR)
_PYTEST_VERBOSE_RE = re.compile(r"^(?P<name>\S+)\s+(?P<status>PASSED|FAILED|SKIPPED|ERROR)\b")


def parse_pytest(log: str) -> dict[str, str]:
    """{test_name -> status} from pytest output (verbose or summary)."""
    out: dict[str, str] = {}
    if not log:
        return out
    for raw in log.split("\n"):
        line = raw.strip()
        if not line:
            continue
        # Summary lines (STATUS first) — checked before verbose so a
        # "PASSED tests/foo.py::test_a" line isn't misread as name=PASSED.
        leading = None
        for st in _PYTEST_STATUSES:
            if line.startswith(st + " ") or line == st:
                leading = st
                break
        if leading is not None:
            work = line
            if leading == FAILED and " - " in work:
                work = work.split(" - ", 1)[0]
            tokens = work.split()
            if len(tokens) < 2:
                continue
            name = tokens[1]
            if name.startswith("[") and name.endswith("]"):  # SKIPPED [N] file:line
                if len(tokens) < 3:
                    continue
                name = tokens[2]
            out[name] = leading
            continue
        # Verbose progress (NAME first, STATUS after)
        m = _PYTEST_VERBOSE_RE.match(line)
        if m:
            name = m.group("name")
            if "::" in name or name.endswith(".py"):
                out[name] = m.group("status")
    return out


_GO_TEST_RE = re.compile(r"^\s*---\s+(?P<status>PASS|FAIL|SKIP):\s+(?P<name>\S+)")
_GO_STATUS = {"PASS": PASSED, "FAIL": FAILED, "SKIP": SKIPPED}


def parse_go_test(log: str) -> dict[str, str]:
    """{test_name -> status} from `go test -v` output."""
    out: dict[str, str] = {}
    if not log:
        return out
    for raw in log.split("\n"):
        m = _GO_TEST_RE.match(raw)
        if m:
            out[m.group("name")] = _GO_STATUS[m.group("status")]
    return out


_CARGO_TEST_RE = re.compile(r"^test\s+(?P<name>\S+)\s+\.\.\.\s+(?P<status>ok|FAILED|ignored)\b")
_CARGO_STATUS = {"ok": PASSED, "FAILED": FAILED, "ignored": SKIPPED}


def parse_cargo_test(log: str) -> dict[str, str]:
    """{test_name -> status} from `cargo test` output."""
    out: dict[str, str] = {}
    if not log:
        return out
    for raw in log.split("\n"):
        m = _CARGO_TEST_RE.match(raw)
        if m:
            out[m.group("name")] = _CARGO_STATUS[m.group("status")]
    return out


_JEST_FILE_RE = re.compile(r"^(?:PASS|FAIL)\s+(?P<path>\S+\.(?:ts|tsx|js|jsx|mjs|cjs))\b")
_JEST_TEST_RE = re.compile(
    r"^(?P<indent>\s*)(?P<glyph>✓|√|✕|×|✗|○|◯)\s+(?P<name>.+?)(?:\s+\(\d+(?:\.\d+)?\s*m?s\))?$"
)
_JEST_GLYPH = {
    "✓": PASSED,
    "√": PASSED,
    "✕": FAILED,
    "×": FAILED,
    "✗": FAILED,
    "○": SKIPPED,
    "◯": SKIPPED,
}


def parse_jest(log: str) -> dict[str, str]:
    """{test_name -> status} from Jest / Mocha / Vitest output."""
    out: dict[str, str] = {}
    if not log:
        return out
    current_file: str | None = None
    describe_stack: list[tuple[int, str]] = []
    last_test_indent: int | None = None
    for raw in log.split("\n"):
        line = raw.rstrip()
        if not line:
            continue
        m = _JEST_FILE_RE.match(line)
        if m:
            current_file = m.group("path")
            describe_stack = []
            last_test_indent = None
            continue
        m = _JEST_TEST_RE.match(line)
        if m:
            indent = len(m.group("indent"))
            name = re.sub(r"^(?:skipped|todo):\s*", "", m.group("name").strip())
            describes = [d for ind, d in describe_stack if ind < indent]
            parts = ([current_file] if current_file else []) + describes + [name]
            out[" > ".join(parts)] = _JEST_GLYPH[m.group("glyph")]
            last_test_indent = indent
            continue
        stripped = line.lstrip()
        if not stripped or stripped.startswith(
            ("Tests:", "Test Suites:", "Snapshots:", "Time:", "Ran all", "●", "→", "✗:")
        ):
            continue
        indent_here = len(line) - len(stripped)
        if current_file and (last_test_indent is None or indent_here < last_test_indent):
            describe_stack = [(i, d) for i, d in describe_stack if i < indent_here]
            describe_stack.append((indent_here, stripped))
    return out


_CTRF_STATUS = {"passed": PASSED, "failed": FAILED, "skipped": SKIPPED, "pending": SKIPPED, "other": ERROR}


def parse_ctrf(payload: str) -> dict[str, str] | None:
    """{test_name -> status} from a CTRF report, or None when malformed.

    CTRF is the trusted channel: the report is written by the pytest plugin,
    not printed to a stream the agent's code can write to. A missing or
    malformed report means the measurement itself failed — callers fail closed.
    """
    try:
        data = json.loads(payload)
        tests = data["results"]["tests"]
        out: dict[str, str] = {}
        for test in tests:
            name = str(test["name"])
            status = _CTRF_STATUS.get(str(test.get("status", "")).lower())
            if status is not None:
                out[name] = status
        return out
    except (KeyError, TypeError, ValueError, AttributeError):
        return None


def detect_runner(test_cmds: str) -> str:
    """Name the test runner a command string invokes.

    Public because the chain controller and terminal verifier both need it to
    agree with this module on how a log should be parsed.
    """
    joined = test_cmds.lower()
    if "pytest" in joined:
        return "pytest"
    if re.search(r"\bgo\s+test\b", joined):
        return "go"
    if re.search(r"\bcargo\s+test\b", joined):
        return "cargo"
    if any(k in joined for k in ("jest", "mocha", "vitest", "npm test", "yarn test", "pnpm test")):
        return "jest"
    return "unknown"


def parse_logs(runner: str, log: str) -> dict[str, str]:
    """Dispatch to the right per-runner parser. Empty dict if unknown."""
    if runner == "pytest":
        return parse_pytest(log)
    if runner == "go":
        return parse_go_test(log)
    if runner == "cargo":
        return parse_cargo_test(log)
    if runner == "jest":
        return parse_jest(log)
    return {}


# ---------------------------------------------------------------------------
# Grading
# ---------------------------------------------------------------------------


def grade(
    fail_to_pass: list[str],
    pass_to_pass: list[str],
    status_map: dict[str, str],
) -> dict:
    """Compute the graded reward + strict resolved bool from a status map.

    f2p_rate   = (# F2P now PASSED) / (# F2P)
    p2p_rate   = (# P2P still PASSED) / (# P2P)   [1.0 when no P2P]
    reward     = f2p_rate * p2p_rate                       (dense training signal)
    resolved   = all F2P pass AND all P2P pass   (SWE-bench TRACKED resolution —
                 the gold patch always satisfies this, preserving the oracle
                 invariant)

    Two distinct EVAL signals (see the audit's "tracked vs command resolved"):
      * `resolved`         — tracked resolution (above). Gold patch -> True.
      * `command_resolved` — stricter: tracked resolution AND the selected test
                             command had NO failures outside F2P/P2P AND exit
                             code 0. Computed in main() where the exit code is
                             known. A benchmark that wants "the whole command
                             passed cleanly" gates on this; SWE-bench-style
                             scoring uses `resolved`.

    `untracked_failed` are FAILED tests in the run that are neither F2P nor
    P2P (e.g. always-failing/flaky tests pulled in by running a whole test
    file). They don't change the graded `reward` or tracked `resolved`, but
    they block `command_resolved` and are recorded for transparency.
    """
    f2p_total = len(fail_to_pass)
    p2p_total = len(pass_to_pass)
    f2p_set = set(fail_to_pass)
    p2p_set = set(pass_to_pass)
    f2p_passed = sum(1 for t in fail_to_pass if status_map.get(t) == PASSED)
    p2p_passed = sum(1 for t in pass_to_pass if status_map.get(t) == PASSED)
    # Tests that should have stayed green but regressed (PASS->not-pass).
    regressions = [t for t in pass_to_pass if status_map.get(t) != PASSED]
    # FAILED tests outside the tracked sets — the selected command isn't clean.
    untracked_failed = sorted(
        t for t, s in status_map.items() if s == FAILED and t not in f2p_set and t not in p2p_set
    )

    f2p_rate = (f2p_passed / f2p_total) if f2p_total else 0.0
    p2p_rate = (p2p_passed / p2p_total) if p2p_total else 1.0
    reward = f2p_rate * p2p_rate
    resolved = f2p_total > 0 and f2p_passed == f2p_total and p2p_passed == p2p_total

    return {
        "reward": round(max(0.0, min(1.0, reward)), 6),
        "resolved": resolved,
        "f2p_total": f2p_total,
        "f2p_passed": f2p_passed,
        "f2p_rate": round(f2p_rate, 6),
        "p2p_total": p2p_total,
        "p2p_passed": p2p_passed,
        "p2p_rate": round(p2p_rate, 6),
        "regressions": sorted(regressions),
        "untracked_failed_count": len(untracked_failed),
        "untracked_failed": untracked_failed[:20],  # cap the list
    }


# ---------------------------------------------------------------------------
# Entry point (invoked by tests/test.sh inside the container)
# ---------------------------------------------------------------------------


def _read_json_list(path: str) -> list[str]:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return [str(x) for x in data] if isinstance(data, list) else []
    except (OSError, ValueError):
        return []


def _read_text(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return ""


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="pr_runtime graded F2P/P2P verifier")
    p.add_argument("--log", required=True, help="captured test-run log file")
    p.add_argument("--f2p", required=True, help="JSON file: FAIL_TO_PASS test names")
    p.add_argument("--p2p", required=True, help="JSON file: PASS_TO_PASS test names")
    p.add_argument("--runner", default="", help="pytest|go|cargo|jest (else auto-detect)")
    p.add_argument("--test-cmds", default="", help="test command string (runner auto-detect)")
    p.add_argument("--exit-code", type=int, default=1, help="test suite exit code (fallback)")
    p.add_argument("--out-dir", default="/logs/verifier", help="where to write reward.{txt,json}")
    p.add_argument(
        "--require-clean-command",
        action="store_true",
        help="training reward is 0 unless exit==0 and no untracked failures",
    )
    p.add_argument(
        "--regression",
        default="",
        help="JSON file: prior-stage F2P tests replayed as the cumulative signal",
    )
    p.add_argument("--regression-log", default="", help="captured log of the regression run")
    p.add_argument(
        "--regression-exit-code", type=int, default=1,
        help="exit code of the regression test command",
    )
    p.add_argument(
        "--ctrf", default="",
        help="CTRF json from the graded run; when set, it is the ONLY status source",
    )
    p.add_argument("--regression-ctrf", default="", help="CTRF json from the regression run")
    args = p.parse_args(argv)

    log = _read_text(args.log)
    f2p = _read_json_list(args.f2p)
    p2p = _read_json_list(args.p2p)
    runner = args.runner.strip() or detect_runner(args.test_cmds)

    # Structured CTRF results from the pytest plugin are the trusted channel:
    # printed test lines can be forged by agent code, the report file cannot.
    # A missing/malformed report yields an empty map, and the empty-parse path
    # below fails closed.
    status_map = (
        parse_ctrf(_read_text(args.ctrf)) or {} if args.ctrf else parse_logs(runner, log)
    )

    if not status_map:
        # Unparseable runner output. With a declared F2P oracle there is no
        # evidence any graded test passed, so the reward fails closed at 0.0;
        # without an oracle (debug emission) the binary exit code is the only
        # signal and is used as a coarse TRAINING fallback.
        # Fail closed when a declared F2P oracle exists: an empty parse then
        # carries no evidence any graded test passed — and in a shared container
        # the agent can manufacture exactly this state (suppress the reporter,
        # force exit status 0) to collect an exit-code payout. Without an oracle
        # (debug emission) the exit code is the only signal, so it stays.
        has_oracle = len(f2p) > 0
        reward = 0.0 if has_oracle else (1.0 if args.exit_code == 0 else 0.0)
        resolved = (args.exit_code == 0) and not has_oracle
        breakdown = {
            "reward": reward,
            "resolved": resolved,
            "command_resolved": bool(resolved and args.exit_code == 0),
            "parse_status": "fallback_exitcode" if not has_oracle else "empty_parse_fail_closed",
            "eval_trustworthy": not has_oracle,
            "runner": runner,
            "f2p_total": len(f2p),
            "p2p_total": len(p2p),
            "exit_code": args.exit_code,
        }
    else:
        breakdown = grade(f2p, p2p, status_map)
        breakdown["parse_status"] = "ok"
        breakdown["runner"] = runner
        breakdown["tests_parsed"] = len(status_map)
        breakdown["exit_code"] = args.exit_code
        # Strict eval signal: tracked resolution AND a clean command (no
        # untracked failures, exit code 0). Benchmarks wanting "the whole test
        # command passed" gate on this; SWE-bench-style scoring uses `resolved`.
        breakdown["command_resolved"] = bool(
            breakdown["resolved"]
            and breakdown["untracked_failed_count"] == 0
            and args.exit_code == 0
        )
        # Training reward gates on a CLEAN command, not just tracked tests:
        # a run that exits nonzero or fails untracked tests pays 0. The tracked
        # product stays in the details for diagnostics. Validation only keeps
        # stages whose gold run is clean, so the oracle still scores 1.0 and a
        # damaged tree (agent broke a neighbor test) cannot earn partial credit.
        tracked = breakdown["reward"]
        breakdown["tracked_score"] = tracked
        if args.require_clean_command:
            if args.exit_code != 0:
                breakdown["reward_gate"] = "test_command_failed"
            elif breakdown["untracked_failed_count"] > 0:
                breakdown["reward_gate"] = "untracked_failures"
            else:
                breakdown["reward_gate"] = "clean"
            reward = tracked if breakdown["reward_gate"] == "clean" else 0.0
            breakdown["reward"] = reward
        else:
            reward = tracked

    regression = _read_json_list(args.regression) if args.regression else []
    if regression:
        if args.regression_ctrf:
            reg_map = parse_ctrf(_read_text(args.regression_ctrf))
            if reg_map is None:
                reg_map = {}
                breakdown["regression_ctrf_failed"] = True
        else:
            reg_map = parse_logs(runner, _read_text(args.regression_log))
        passed = sum(1 for t in regression if reg_map.get(t) == PASSED)
        # The cumulative signal: whether behaviour earned by EARLIER stages
        # still works. Replayed tests legitimately fail at gold when later
        # history changed them (measured: oracle rate ≈ 0.99), so the RATE is
        # the signal — but the command itself must be sound: exit 0 or 1 and
        # something parsed. Collection errors (exit 2+) or an empty parse mean
        # the measurement is broken, which fails the maintenance reward closed.
        rate = passed / len(regression)
        breakdown["regression_total"] = len(regression)
        breakdown["regression_passed"] = passed
        breakdown["regression_rate"] = round(rate, 6)
        breakdown["regression_command_clean"] = (
            args.regression_exit_code in (0, 1)
            and bool(reg_map)
            and not breakdown.get("regression_ctrf_failed", False)
        )

    os.makedirs(args.out_dir, exist_ok=True)
    if regression and args.require_clean_command:
        # The primary reward: local work only counts when it didn't break
        # earlier work. All gates fail closed.
        transition_ok = True  # carry failures never reach this process
        local_clean = breakdown.get("reward_gate") == "clean"
        reg_clean = breakdown["regression_command_clean"]
        if transition_ok and local_clean and reg_clean:
            maintenance = round(breakdown["tracked_score"] * breakdown["regression_rate"], 6)
        else:
            maintenance = 0.0
        breakdown["maintenance_reward"] = maintenance
        breakdown["local_score"] = breakdown["tracked_score"]
        breakdown["regression_score"] = breakdown["regression_rate"]
        breakdown["reward"] = maintenance
        reward = maintenance
    with open(os.path.join(args.out_dir, "reward.txt"), "w", encoding="utf-8") as f:
        f.write(f"{reward:.6f}\n")
    if regression:
        # Multi-key reward: Harbor averages each key across steps, so the
        # local and maintenance signals arrive side by side.
        with open(os.path.join(args.out_dir, "reward.json"), "w", encoding="utf-8") as f:
            json.dump(
                {
                    "reward": reward,
                    "local_score": breakdown.get("local_score", breakdown["reward"]),
                    "regression_score": breakdown["regression_rate"],
                },
                f,
            )
    with open(os.path.join(args.out_dir, "reward-details.json"), "w", encoding="utf-8") as f:
        json.dump(breakdown, f, indent=2)

    print(json.dumps(breakdown, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "detect_runner",
    "grade",
    "main",
    "parse_cargo_test",
    "parse_go_test",
    "parse_jest",
    "parse_logs",
    "parse_pytest",
]
