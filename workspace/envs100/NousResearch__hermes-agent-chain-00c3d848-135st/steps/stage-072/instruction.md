**fix(website): auto-wrap ASCII-art code blocks in generated skill pages**

.

## Summary
The generator in `website/scripts/generate-skill-docs.py` now wraps fenced code blocks that contain Unicode box-drawing chars with `` markers, so `docs-site-checks` can't fail on a skill's own ASCII diagram.

Root cause: `ascii-guard` scans inside fenced code blocks. A skill diagram whose box dimensions don't add up (extra chars after right border, too-short line, etc.) fails lint even though the block is purely verbatim text.

## Changes
- `website/scripts/generate-skill-docs.py`: `mdx_escape_body` now feeds code segments through `_wrap_ascii_art_code_blocks()`, which adds ignore markers only if the segment contains box-drawing chars. Plain bash/python code blocks stay uncluttered.
- `tests/website/test_generate_skill_docs.py`: 6 tests — plain code not wrapped, box code wrapped, mixed-block discrimination, tilde fences, pre-wrapped source stays harmless, char-set smoke.

## Validation
| | Without patch | With patch |
|---|---|---|
| Current main (source has ignore markers from #15260) | 0 errors | 0 errors |
| Source markers reverted (simulates pre-fix world) | 4 errors (L46/54/157 on 2 pages) | 0 errors |
| Targeted tests | — | 6/6 pass in 0.35s |

No committed-page regeneration needed — CI re-runs `extract-skills` + `generate-skill-docs` before linting, so the generator change alone fixes the workflow. Credits: @perlowja (filed #15305), @pickettaustin (landed same-day source-side mitigation #15260).