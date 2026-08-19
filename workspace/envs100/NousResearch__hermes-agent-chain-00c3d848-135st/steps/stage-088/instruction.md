**feat: trigram FTS5 index for CJK search, replace LIKE fallback**

## Summary

Replaces the `LIKE '%query%'` full-table-scan fallback for CJK queries with a proper **trigram FTS5 index** (`messages_fts_trigram`). Builds on top of #16276.

## What changed

| Component | Change |
|---|---|
| `FTS_TRIGRAM_SQL` | New trigram FTS5 virtual table + INSERT/UPDATE/DELETE triggers |
| Schema v10 migration | Creates the trigram table, backfills existing messages |
| `_init_schema()` | Probes for trigram table on fresh DBs (same pattern as `messages_fts`) |
| `_is_cjk_codepoint()` / `_count_cjk()` | New helpers to count CJK characters in a query |
| `search_messages()` | 3+ CJK chars -> trigram FTS5 MATCH (indexed, ranked, snippets); 1-2 CJK chars -> LIKE fallback (trigram needs >= 9 UTF-8 bytes) |

## Why

The LIKE fallback in #16276 is correct but is a full table scan with no ranking. The trigram tokenizer (built into SQLite since 3.34.0) creates overlapping 3-byte sequences so substring matching works natively for any script -- CJK, Thai, etc. This gives us:

- **Indexed lookups** instead of table scans
- **FTS5 ranking** (BM25) instead of timestamp ordering
- **Proper snippets** with `>>>` / `<<<` markers instead of `substr()` hacks

The 1-2 CJK character LIKE fallback remains because the trigram tokenizer needs at least 3 CJK characters (9 UTF-8 bytes) for a match.

## Before / After

| Scenario | #16276 (LIKE) | This PR (trigram) |
|---|---|---|
| CJK query, 3+ chars | LIKE `%query%` (table scan) | `messages_fts_trigram MATCH` (indexed) |
| CJK query, 1-2 chars | LIKE `%query%` (table scan) | LIKE `%query%` (same -- trigram cannot match) |
| CJK query with `%` / `_` | LIKE with ESCAPE | FTS5 MATCH (double-quoted, no escaping needed) |
| English query | FTS5 (unchanged) | FTS5 (unchanged) |
| Snippets (CJK) | `substr(content, instr-40, 120)` | `snippet(messages_fts_trigram, ...)` |
| Ranking (CJK) | `ORDER BY timestamp DESC` | `ORDER BY rank` (BM25) |

## Migration

Schema v10 runs automatically on first open. Creates the trigram table and backfills from existing messages. Triggers keep it in sync going forward.