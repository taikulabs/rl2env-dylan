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

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/skills/test_memento_cards.py`
- `tests/skills/test_youtube_quiz.py`