**fix(session_search): coerce limit to int to prevent TypeError with non-int values**

## Summary

Models (especially open-source like qwen3.5-plus) may send non-int values for the `limit` parameter — `None` (JSON null), a string, or even a type object. This caused:

```
TypeError: '<=' not supported between instances of 'int' and 'type'
```

when the value reached `min()`/comparison operations in `session_search()`.

## Changes

- Add defensive `int` coercion at `session_search()` entry with fallback to default 3
- Clamp limit to [1, 5] range (previously only capped at 5, not floored at 1)
- Add 4 tests: `None`, type object, string, and negative/zero limit values

## Context

Reported by community user ludoSifu via Discord — running Hermes with qwen3.5-plus through a custom provider path. The diagnostic logs confirmed the TypeError is real and reproducible.