**feat(skills): add memento-flashcards optional skill**

Adds a spaced-repetition flashcard system as an optional skill under `optional-skills/productivity/`.

**Features:**
- Create flashcards from facts (explicit or implicit intent detection)
- Review due cards with free-text answers graded by the agent
- Spaced repetition scheduling (hard +1d, good +3d, easy +7d, auto-retire after 3 easys)
- Generate quiz decks from YouTube transcripts
- CSV import/export, collection management, stats
- Atomic file writes, deduplication by video ID

**Includes:** 47 tests across 8 test classes covering CRUD, scheduling, CSV roundtrip, edge cases, corrupt JSON recovery.

Cherry-picked from PR #1853 by @magnusahmad with authorship preserved. Follow-up fix: use `HERMES_HOME` env var instead of hardcoded `~/.hermes` for profile safety.