**fix(delegation): budget subagent summaries against parent context headroom**

## Summary
Subagent summaries can no longer overflow the parent's context window: `delegate_task` now caps each summary against the parent's *remaining* context headroom (split across the batch) and, when it must trim, falls back to the same head+tail/spill-to-file pattern `web_extract` uses for large pages — so nothing is lost.

Root cause: batch fan-out returned every child's full `final_response` verbatim into the parent's context. A 4-5 child batch could dump 60k+ tokens at once, exceeding the parent window and — on rate-limited providers — triggering a compression/429 death spiral (429 misread as context-too-large → window step-down → retry loop → conversation dies).

## Changes
- `tools/delegate_tool.py`:
  - `_apply_summary_budget()` — runs once after batch aggregation (covers single-task AND batch paths). Effective per-summary cap = `min(dynamic headroom budget, static ceiling)`.
  - `_parent_summary_char_budget()` — sizes the cap as `(remaining parent headroom × 0.5) ÷ batch_size`. Caps the *real* resource (N summaries at once), not a magic char count. Floors at 2000; returns `None` (→ static-ceiling-only) when parent context state is unknown.
  - `_trim_summary_with_footer()` — mirrors `web_extract._truncate_with_footer`: a **head+tail window** (75/25, line-snapped) so the subagent's opening AND closing (outcomes / files-changed / issues, which live at the end) both survive, plus a footer with the exact `read_file offset=` to page the omitted middle.
  - `_spill_summary_to_file()` — mirrors `web_extract._store_full_text`: writes the full text to `cache/delegation`, registered in `_CACHE_DIRS` so it mounts read-only into remote backends (Docker/Modal/SSH). The parent recovers full detail with `read_file` on any backend.
  - Tightened the child system prompt (lead with outcomes, bullets).
- `tools/credential_files.py`: register `cache/delegation` in `_CACHE_DIRS`.
- `hermes_cli/config.py`: `delegation.max_summary_chars` (default 24000) static ceiling; `0` disables it.
- `scripts/release.py`: AUTHOR_MAP entry for the original contributor.

## Why this shape (vs. a flat char cap)
The original PR truncated every summary at a hardcoded 4000 chars head-only, which mutilates a legitimate single deep-delegation child (a 12k-char code review loses 2/3 of its output, and head-only drops the conclusions at the end). This version caps the aggregate that actually overflows the parent, keeps both ends of the summary, and loses nothing — full text is recoverable from the spill file, exactly like a large web page.

## Validation
| | Behavior |
|---|---|
| Small summaries | pass through untouched |
| Batch overflow (5×60k, parent 120k/131k) | trimmed to ~2.6k each; head AND tail survive in-context; full text in `cache/delegation`; `read_file offset=` footer present |
| Dynamic scaling | N=1→186k · N=5→37k · N=20→9.3k chars |
| Parent over budget | floor (2000) enforced |
| No compressor / unknown ctx | falls back to static ceiling; both disabled → no trim |

7 new budget tests + 144 existing delegation tests + 266 credential/docker/platform tests green; E2E (head+tail + spill + offset-footer + recover) verified with real imports against a temp `HERMES_HOME`.

Salvages and re-architects #9126 by @rc-int — credit preserved via `Co-authored-by`.

## Infographic
![Subagent summary budget](https://v3b.fal.media/files/b/0aa0597d/6HmH4G8DZyf9DD6-_31Cj_pNrPfrlc.png)