**fix(anthropic): send fast mode speed via extra_body**

## Summary

Salvage of #9216 by @bobashopcashier. Cherry-picked onto current main.

Fixes Anthropic fast mode crash on native Opus — `speed="fast"` was passed as a top-level SDK kwarg, but the Anthropic SDK requires it via `extra_body`. Moves `speed` into `extra_body` dict.

## Changes
- Route `speed` through `extra_body["speed"]` in `build_anthropic_kwargs()`
- Update test assertions + add regression test