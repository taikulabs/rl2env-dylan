**fix(cron): treat non-dict origin as missing instead of crashing tick**

Salvage of #19013 by @Tranquil-Flow onto current main. Closes the non-dict-origin sub-bug from #18722 where a job whose `origin` field holds a free-form string (e.g. migration tag) crashes every tick with `AttributeError: 'str' object has no attribute 'get'` and never recovers.

## Changes
- `cron/scheduler.py`: `_resolve_origin` guards `isinstance(origin, dict)` instead of bare truthiness (+11/-2)
- `tests/cron/test_scheduler.py`: parametrized `test_non_dict_origin_returns_none_instead_of_crashing` over str/int/list/tuple/float (+24)

## Validation
- TestResolveOrigin: 10/10 pass
- 3 TestSilentDelivery failures are pre-existing on current main (same failures without this change), unrelated to cron origin handling

. Related #18722. Sibling sub-bug (recurring-job recovery) tracked in #18825 as the PR notes.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/cron/test_scheduler.py`