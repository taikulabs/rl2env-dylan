**fix: enforce TTL in MessageDeduplicator + use yaml for gateway --config**

## Summary

Two targeted gateway fixes:

### 1. MessageDeduplicator TTL enforcement

`is_duplicate()` returned `True` for any previously seen message ID without checking its age. Expired entries were only purged when cache size exceeded `max_size`. On normal workloads that never overflow, message IDs stayed "duplicate" forever — a message from 3 hours ago would still be rejected if seen again, even with a 5-minute TTL.

**Fix:** Check `now - timestamp < ttl` before returning True. Expired entries are deleted and the message is treated as new.

**Before:**
```python
if msg_id in self._seen:
    return True  # Always duplicate, regardless of age
```

**After:**
```python
if msg_id in self._seen:
    if now - self._seen[msg_id] < self._ttl:
        return True
    del self._seen[msg_id]  # Expired — allow through
```

### 2. Gateway --config uses yaml.safe_load()

The `--config` CLI flag in `gateway/run.py main()` used `json.load()` to parse config files. YAML is the only documented format and every other config loader uses `yaml.safe_load()`. Passing a YAML config crashed with `json.JSONDecodeError`.

**Fix:** Replace `json.load()` with `yaml.safe_load()`. One-line change.

## Tests

7 new tests for MessageDeduplicator in `tests/gateway/test_message_deduplicator.py`:
- TTL enforcement (within window = dup, after expiry = not dup)
- Entry refresh after expiry
- Independent message IDs
- Empty ID handling
- Max-size eviction of expired entries
- TTL=0 edge case