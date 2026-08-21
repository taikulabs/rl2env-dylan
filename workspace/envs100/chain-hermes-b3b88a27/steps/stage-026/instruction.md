**fix(honcho): improve conclude descriptions and add exactly-one validation**

## Summary

Improve `honcho_conclude` tool descriptions and add runtime exactly-one validation.

The `anyOf` removal was already merged. This adds what the duplicate PRs contributed on top: clearer descriptions that explicitly tell the model not to send both params, runtime validation rejecting calls with both or neither of `conclusion`/`delete_id`, a schema regression test, and a both-params rejection test.

Consolidates #10847 (@ygd58), #10864 (@cola-runner), #10870 (@vominh1919), #10952 (@ogzerber).

| PR | Contribution taken |
|----|-------------------|
| #10847 @ygd58 | Issue report that kicked this off |
| #10864 @cola-runner | Schema regression test pattern |
| #10870 @vominh1919 | Test assertions |
| #10952 @ogzerber | Runtime exactly-one validation, improved descriptions, both-params test |

## Test Results

```
tests/honcho_plugin/test_session.py::TestConcludeToolDispatch  8 passed
```

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/honcho_plugin/test_session.py`