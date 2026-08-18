**fix: escape parens and braces in fork bomb regex pattern**

## Summary
- cherry-pick PR #1078's fork-bomb regex fix onto current main with authorship preserved
- add the contributor's targeted regression tests for the classic `:(){ :|:& };:` form, a whitespace variant, and a safe colon-containing command

## Contributor credit
Salvages PR #1078 by cherry-picking the contributor commit onto current main with authorship preserved.