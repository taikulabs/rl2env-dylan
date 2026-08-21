**fix(discord): flat /skill command with autocomplete — fits 8KB limit trivially**

, .

## Problem

The nested `/skill` command group (category subcommand groups × skill subcommands) serialized to ~14 KB with the default 75-skill catalog, exceeding Discord's ~8000-byte per-command registration payload. `tree.sync()` rejected the entire slash-command batch with error 50035 — ALL slash commands including the 27 base commands (`/model`, `/background`, `/new`, …) failed to register. Every default Hermes Discord install was broken.

## Fix

Replace the nested Group layout with a single flat Command:

```
/skill name:<autocomplete>  args:<optional string>
```

**Autocomplete options are fetched dynamically by Discord when the user types — they do NOT count against the per-command registration budget.** So this single command registers at ~200 bytes regardless of how many skills exist. Scales to thousands of skills with no size calculations, no splitting, no hidden skills.

UX improvements:
- Discord live-filters by the user's typed prefix against **both** name and description — `/skill pdf` finds `ocr-and-documents` via its description. More discoverable than clicking through 19 category submenus.
- Unknown skill name → ephemeral error pointing the user at autocomplete.
- Stable alphabetical ordering across restarts.

## Why not the other proposed approaches

Three prior PRs tried to fit within 8 KB by modifying the nested layout:

- **#10214 (@njiangk)**: truncated all descriptions to `Run <name>` and category descriptions to `Skills`. Works, but destroys slash-picker UX — 80 entries all say "Run X".
- **#11385 (@LeonSGP43)**: 40-char description clamp + iterative trim-largest-category fallback. Works, but HIDES skills the user can no longer invoke via slash — functional regression.
- **#10261 (@zeapsu)**: adaptive split into `/skill-<cat>` top-level groups. Preserves all skills but pollutes the slash namespace with 20+ top-level commands.

All three work around the symptom. The flat-autocomplete design **dissolves** the problem — there is no payload-size pressure to manage in the first place.

## Tests

New in `tests/gateway/test_discord_slash_commands.py` (5 cases replace 3 nested-structure tests):

- flat-not-nested structure assertion
- empty skills → no command registered
- callback dispatches the right `cmd_key` by name
- unknown name → ephemeral error, no dispatch
- **large-catalog regression guard (500 skills)** — command registration payload stays under 500 bytes regardless of catalog size

## E2E validation (real discord.py 2.7.1)

Confirmed live in a sandboxed environment:
- Command registers as `discord.app_commands.Command` (not Group).
- Autocomplete filter works for name queries (`gif` → `gif-search`) AND description queries (`pdf` → `ocr-and-documents`, `note` → `obsidian`).
- 500-skill catalog correctly capped at 25 results per autocomplete query (Discord's hard cap), with substring filter applied.
- Choice labels formatted as `name — description`, clamped to Discord's 100-char limit.
- Full callback dispatch path: `/skill gif-search` → `_run_simple_slash("/gif-search")`.
- `/skill non-existent` → ephemeral error reply.

## Attribution

Credit to all three PR authors who proposed workarounds for the same bug (#10214 @njiangk, #11385 @LeonSGP43, #10261 @zeapsu) and both issue reporters (#11321 @BonsaiEX, #10259 @zeapsu). Their analyses surfaced the 8KB payload math that shaped this fix. The three alternative PRs will be closed with explanatory comments linking here.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_discord_slash_commands.py`