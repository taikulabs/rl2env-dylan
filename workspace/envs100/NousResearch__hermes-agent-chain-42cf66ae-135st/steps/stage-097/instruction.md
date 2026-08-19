**fix: expand environment blocklist for terminal isolation**

## Summary
- 
- add regression coverage for the newly blocked non-registry provider env vars so they are both present in the blocklist and stripped from subprocess environments

## Contributor credit
Salvages PR #1384 by cherry-picking the contributor commit onto current main with authorship preserved, plus a small current-main test follow-up.
