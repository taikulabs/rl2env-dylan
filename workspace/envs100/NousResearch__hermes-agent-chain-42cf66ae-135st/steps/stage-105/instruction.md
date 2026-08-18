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