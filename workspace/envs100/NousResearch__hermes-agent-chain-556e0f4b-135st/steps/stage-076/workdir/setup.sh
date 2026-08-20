#!/bin/bash
# Harbor step setup: hygiene + carry. Runs before the agent phase.
set -uo pipefail
# Remove the previous step's grader before the agent starts (Harbor only
# empties these right before verification).
rm -rf /logs/verifier /tests 2>/dev/null || true
cd /workspace || exit 1
git config --global --add safe.directory /workspace
CARRY="$(dirname "$0")/carry.diff"
[ -s "$CARRY" ] || exit 0
# Tolerate hunks already present: an agent may have written equivalent
# code, and a partly-applied carry is better than a failed step setup.
# A --reject fallback leaves a degraded tree the stage oracle was never
# validated against, so that outcome is recorded, never silent: the
# marker travels with the workspace artifact into grading.
DEGRADED=/workspace/.r2e_carry_degraded.json
rm -f "$DEGRADED"
if git apply --verbose "$CARRY"; then
  exit 0
elif git apply --verbose --3way "$CARRY"; then
  exit 0
fi
git apply --verbose --reject "$CARRY" || true
python3 -S - "$DEGRADED" <<'PYEOF'
import json, sys
from pathlib import Path
rej = sorted(str(p) for p in Path('.').rglob('*.rej'))
Path(sys.argv[1]).write_text(json.dumps({
    'degraded': True,
    'reason': 'carry patch applied with rejects; tree never validated',
    'rejected_files': rej,
}))
PYEOF
# Place this stage's graded tests (staged by the step's workdir upload) after
# the carry, so a carry that touched the same files cannot clobber them.
if [ -d /workspace/.r2e/tests ]; then
  (cd /workspace/.r2e/tests && find . -type f -print0) | \
    while IFS= read -r -d "" rel; do
      mkdir -p "/workspace/$(dirname "$rel")"
      cp "/workspace/.r2e/tests/$rel" "/workspace/$rel"
    done
fi
exit 0
