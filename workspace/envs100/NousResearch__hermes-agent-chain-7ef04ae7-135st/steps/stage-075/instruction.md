**fix(security): cover Move and no-space headers in patch_tool sensitive path check**

## Summary

Closes two bypass gaps in `patch_tool`'s sensitive-path pre-check (the regex that extracts V4A patch paths so `/etc/*`, `/boot/*`, `/usr/lib/systemd/*` etc. are refused before they reach the low-level file ops). Both let a crafted patch parse and apply while skipping the broad pre-check, falling back on the much narrower `file_operations` deny list — a persistence vector on a root-running gateway (e.g. `/etc/crontab`, `/etc/profile.d/x.sh`).

Original work by @0xbyt4, salvaged onto current `main` and widened.

## Changes

- `tools/file_tools.py`:
  - **Gap 1 — Move never extracted.** `*** Move File: src -> dst` is a valid V4A op (`patch_parser.py:114`) but the extraction regex only matched `Update|Add|Delete`. Added a Move regex that checks **both** endpoints.
  - **Gap 2 — `\s+` vs `\s*`.** The pre-check required a space after `***`, but the parser uses `\s*` — so `***Update File: /etc/hosts` parsed/applied while skipping the check. Loosened to `\s*`.
  - **Widening (sibling gap on current main):** main gained a `..` traversal rejection inside the Update/Add/Delete loop after this PR was opened. The new Move endpoints now run through that **same** traversal rejection, so a Move to `../../../etc/shadow` is refused too.

- `tests/tools/test_file_tools.py`: new `TestPatchSensitivePathExtraction` — Move→/etc dst blocked, Move←/etc src blocked, no-space `***Update` blocked, Move `..` traversal blocked, safe `/tmp→/tmp` Move still dispatches.

No behavior change for safe patches — only adds paths to the pre-check; nothing is relaxed.

## Validation

| Vector | Before | After |
|---|---|---|
| `*** Move File: x -> /etc/crontab` | applied (fell to narrow deny list) | refused: sensitive path |
| `*** Move File: /etc/hosts -> x` | applied | refused: sensitive path |
| `***Update File: /etc/resolv.conf` (no space) | applied | refused: sensitive path |
| `*** Move File: x -> ../../../etc/shadow` | applied | refused: `..` traversal |
| `*** Move File: /tmp/a -> /tmp/b` (safe) | applied | applied (unchanged) |

48 tests pass in `tests/tools/test_file_tools.py`. E2E verified with real `patch_tool` against real `/etc` targets — all four vectors blocked at the pre-check, nothing touched disk.

## Infographic

![patch_tool sensitive-path bypass closed](https://v3b.fal.media/files/b/0aa0593f/vDh5Ku_c38nwJYj_fR5L-_CXNfvXxF.png)

Nous Research