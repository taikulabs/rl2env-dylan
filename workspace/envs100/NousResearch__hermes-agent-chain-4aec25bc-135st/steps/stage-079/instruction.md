**fix(cli): preserve cron asterisks in strip mode**

Salvage of #28019 by @felix-windsor.

**What:** `_strip_markdown_syntax()` treated any line of 3+ asterisks as a Markdown horizontal rule and stripped it. Cron expressions like `* * * * *` (5 asterisks separated by spaces) matched the HR pattern and were silently removed from agent output. The single-emphasis stripper `*text*` also chewed up bare asterisks.

**How:**
- Split the HR regex: `-` and `_` still strip on 3+, but `*` only strips on *exactly 3* (the canonical CommonMark form `* * *`).
- Tighten the `*emphasis*` regex to require non-whitespace at both inner edges, so `* * * * *` no longer matches as five emphasis groups.
- Test added covering both: cron expression preserved AND `* * *` HR still stripped.

Original PR: 
.