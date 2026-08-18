**fix(terminal): prevent heredoc fence wrapper leak in oneshot execution (salvage #3508)**

## Summary
Salvage of #3508 by @kshitijk4poor. Cherry-picked onto current main with authorship preserved.

The oneshot terminal wrapper in `LocalEnvironment._execute_oneshot` joined the user command with fence markers using `;` on a single line. When the user command ends with a heredoc (e.g. `gh issue create --body <<'EOF'...EOF`), the closing delimiter must be alone on its line — the trailing `; __hermes_rc=$?` broke the delimiter, causing bash to treat the rest of the wrapper script as heredoc body. This leaked `__hermes_rc`, `__HERMES_FENCE`, and `exit` text into captured stdout.

Fix: switch from `;` separators to `\n` separators so the post-command trailer always starts on its own line.

## Changes
- `tools/environments/local.py`: newline-separated wrapper instead of semicolon-joined
- New test: `test_oneshot_heredoc_does_not_leak_fence_wrapper`

## Verification
- Unit tests: 26/26 pass in `test_local_persistent.py`
- Live PTY test: heredoc commands produce clean output with no fence leakage
- Regression: regular (non-heredoc) commands unaffected

## Credit
Original work by @kshitijk4poor in #3508.