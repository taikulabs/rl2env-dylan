**fix(gateway): prevent Telegram photo burst interrupts**

## Summary
- batch non-album Telegram photo bursts before they hit the gateway so rapid multi-photo sends become one logical event
- queue photo follow-ups behind active runs instead of interrupting them at the adapter and gateway priority-interrupt layers
- add stronger regression coverage for the reproduced failure modes, including non-album bursts and photo priority interrupts

## Reproduction
I reproduced the bug on current main with focused gateway tests before applying the fix:
- photo follow-ups during an active adapter session set the interrupt flag
- non-album Telegram photo bursts forwarded each photo immediately instead of batching
- the gateway priority path called the running agent interrupt hook for photo events

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_interrupt_key_match.py`
- `tests/gateway/test_telegram_documents.py`
- `tests/gateway/test_telegram_photo_interrupts.py`