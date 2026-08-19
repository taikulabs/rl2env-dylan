**fix(gateway): defer background review notifications until after main reply**

## Summary

Salvage of PR #10541 by @g-guthrie with architectural improvements.

Background review notifications (`💾 Skill created`, `💾 Memory updated`) could race ahead of the main assistant reply in chat, making it look like the agent searched, created a skill, and then stopped.

### What changed

Gate bg-review notifications behind a `threading.Event` + pending queue inside `run_sync()`. The release callback is registered on the adapter's new `_post_delivery_callbacks` dict so `base.py`'s `finally` block fires it after the main response is delivered.

### Changes from original PR

- **Removed `__self__` coupling** — Original PR had `base.py` reaching through `getattr(self._message_handler, "__self__", None)` to find the GatewayRunner. Replaced with a clean `_post_delivery_callbacks` dict on the adapter itself (a general-purpose hook, not GatewayRunner-specific).
- **Removed GatewayRunner-level infrastructure** — No more `_deferred_bg_review_releases` dict, `_deferred_bg_review_lock`, `_register_deferred_background_review_release()`, or `_release_deferred_background_reviews()` methods. 24 fewer lines of production code.
- **Fixed type annotation** — `Dict[str, Callable]` instead of `Dict[str, Any]`.
- **Cleaner test** — Adapter-level callback test instead of reaching through handler `__self__`.

### Files changed

- `gateway/platforms/base.py` — `_post_delivery_callbacks` dict in `__init__`, pop+call in `finally`
- `gateway/run.py` — Event/pending/lock gating in `run_sync()`, adapter registration, queued-message release
- `tests/gateway/test_run_progress_topics.py` — BackgroundReviewAgent + 2 new tests