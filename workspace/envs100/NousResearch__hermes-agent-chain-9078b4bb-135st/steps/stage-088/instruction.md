**feat(agent): one-shot LLM helper + llm.oneshot gateway RPC**

## Summary
A **one-shot** is a single stateless model call that runs *outside* any conversation: it never touches session history, never breaks prompt caching, and returns plain text. UI surfaces need this for small generative chores — a commit message from a diff, a rename suggestion, a summary — where spinning up an agent turn would pollute the thread and hand-rolling an LLM call at every call site would be worse.

- **`agent/oneshot.py`** — `run_oneshot(...)` over the existing auxiliary-client plumbing (same path as title generation). Two call shapes:
  - explicit `instructions` / `user_input`, or
  - a registered `template` + `variables` (templates own the prompt engineering so it stays consistent across CLI/TUI/desktop).
  Ships a `commit_message` template. Model selection inherits the live session via `main_runtime`, else the configured auxiliary `task` backend. Strips a wrapping code fence; raises `KeyError` (unknown template) / `ValueError` (empty prompt) loudly.
- **`tui_gateway/server.py`** — `llm.oneshot` RPC (registered as a long-handler) that inherits the session's model when `session_id` resolves, else falls back to the aux backend.

Stateless by construction — no session mutation, prompt cache untouched. First consumer is the desktop review pane's "generate commit message", but it's surface-agnostic.