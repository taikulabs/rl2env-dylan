**fix(learn): honor requirements mixed with sources in /learn requests**

## Summary
`/learn` now honors requirements that are mixed in with sources — when a request leads with a path or link, the trailing prose ("focus on auth, skip deprecated") is treated as authoring guidance instead of being dropped.

Root cause: not a parser bug. Both CLI (`split(None, 1)`) and gateway (`get_command_args()`) already capture the full free-text argument. The gap was in `build_learn_prompt`, which dumped the request as one undifferentiated source blob, so the agent fetched the first source and ignored the rest. (Reported by @GrenFX.)

## Changes
- `agent/learn_prompt.py`: prompt now tells the agent the `/learn` request may mix **sources** (dirs, paths, URLs, "what we just did", notes) and **requirements** (focus, scope, what to omit, naming) in any order; prose after a path/link is authoring guidance to honor, not noise; "never fetch the first source and ignore the rest." New step 1b: apply every requirement to what the SKILL.md covers, not just which sources get read.
- `tests/agent/test_learn_prompt.py`: new `test_separates_sources_from_requirements` — leading-URL + trailing-prose request, asserts the prose survives verbatim and the prompt names the sources/requirements split.

Both CLI `/learn` and gateway `/learn` share `build_learn_prompt`, so both inherit the fix. No parser change, zero tool footprint.

## Validation
| | Before | After |
|---|---|---|
| `/learn <url> focus on auth` | URL fetched, focus dropped | URL gathered AND focus applied to the skill |
| Targeted tests | 12 | 13/13 passing |

## Infographic
![/learn sources and requirements](https://v3b.fal.media/files/b/0aa06ef7/1CP46iLi3DrRJm0aDFixQ_WFh1XUx5.png)