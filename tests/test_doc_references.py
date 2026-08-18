"""Grep gate: docs and docstrings must not reference modules that do not exist.

The pr_chain migration shipped four dead module references (`_pr_chain_controller.py`,
`_pr_chain_verifier.py` in CLAUDE.md, stale names in docs). A module path in
backticks reads as a fact about the codebase; this test makes that checkable.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src" / "repo2rlenv"

# Backticked tokens that name a repo2rlenv module, either dotted
# (`repo2rlenv.pipelines.pr_chain`) or as a path (`repo2rlenv/pipelines/x.py`),
# plus bare `_underscore.py` tokens (architecture-tree listings). Bare names
# without an underscore (`task_module.py`) are product nouns, not repo paths.
# docs/rfcs/ is exempt: RFCs are dated design records and may reference planned
# or retired modules.
DOTTED = re.compile(r"^repo2rlenv\.[\w.]+$")
PATHY = re.compile(r"^(?:src/)?repo2rlenv/[\w/.]+\.py$")
BARE_PY = re.compile(r"^_[\w]+\.py$")


def _module_exists(token: str) -> bool:
    if DOTTED.match(token):
        # Resolve the longest module prefix; the tail may be a function or
        # class inside that module.
        parts = token.removeprefix("repo2rlenv.").split(".")
        for cut in range(len(parts), 0, -1):
            rel = "/".join(parts[:cut])
            if (SRC / f"{rel}.py").exists() or (SRC / rel / "__init__.py").exists():
                return True
        return False
    if PATHY.match(token):
        rel = token.removeprefix("src/").removeprefix("repo2rlenv/")
        return (SRC / rel).exists()
    if BARE_PY.match(token):
        return any(SRC.rglob(token))
    return True  # not a module reference


def _tokens():
    docs = [REPO_ROOT / "CLAUDE.md", REPO_ROOT / "README.md", *REPO_ROOT.glob("docs/**/*.md")]
    for doc in docs:
        # RFCs are dated design records (planned/retired names); RELATED_WORK
        # is a provenance table naming other projects' files.
        if doc.is_relative_to(REPO_ROOT / "docs" / "rfcs"):
            continue
        if doc.name == "RELATED_WORK.md":
            continue
        for token in re.findall(r"`([^`]+)`", doc.read_text(encoding="utf-8")):
            yield doc, token
    for py in SRC.rglob("*.py"):
        for token in re.findall(r"`([^`]+)`", py.read_text(encoding="utf-8")):
            yield py, token


def test_no_dead_module_references():
    dead = [
        f"{doc.name}: `{token}`"
        for doc, token in _tokens()
        if not _module_exists(token)
        # data tokens: flags, env vars, CLI invocations, placeholders
        and " " not in token
        and not token.startswith("-")
    ]
    assert not dead, "references to modules that do not exist:\n" + "\n".join(dead)
