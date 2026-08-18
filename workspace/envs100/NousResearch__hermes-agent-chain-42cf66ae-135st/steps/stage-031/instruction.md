**feat: improve context compaction handoff summaries**

## Summary
- adapt the core idea from #916 onto current main's call_llm-based context compressor
- replace the old bare context-summary marker with a clearer handoff wrapper that explains earlier work may already be reflected in current session state
- update the compaction summarization prompt to produce resume-oriented handoff summaries and add normalization/tests for legacy and current prefixes