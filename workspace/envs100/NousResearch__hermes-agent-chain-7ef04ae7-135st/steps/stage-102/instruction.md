**fix(tui): float petdex pet on the status bar + responsive text reservation**

## Summary
Reworks the TUI petdex mascot so it sits in a low bottom-right corner without eating a full-width row or slicing transcript text.

- **Placement** — the pet is now a small **floating overlay** riding the bottom-right corner just above the status bar (`position="absolute"`), instead of a full-width band that reserved a whole row. It reserves no layout rows; the transcript scrolls underneath.
- **Readability, responsively** — the pet publishes its footprint via a tiny `$petBox` store and the transcript keeps text clear of it based on width:
  - **wide** terminals → reserve a **right gutter** so lines wrap to the pet's left;
  - **narrow** terminals → collapse to **reserved bottom rows** so full-width lines sit above it.
- **Kitty rendering fix** — kitty fits an image to its cell rect preserving aspect, so a frame that isn't a whole multiple of the cell rounded up and the terminal **clipped the feet / letterboxed a blank row**. Frames are now alpha-trimmed and **snapped to a whole cell grid** before transmit, so the sprite renders full-body (see ). Works in Ghostty/kitty; unicode half-block fallback unchanged.

## Commits
1. `fix(pet): snap kitty frames to whole cells`
2. `feat(tui): add $petBox store for the pet's footprint`
3. `feat(tui): float petdex pet bottom-right with responsive text reservation`