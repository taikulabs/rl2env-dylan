**fix(acp): declare session load and resume capabilities in initialize response**

## What does this PR do?

The ACP `initialize` response only advertised `fork` and `list` session capabilities, but `load_session()` and `resume_session()` were already fully implemented. ACP clients (e.g. Zed) check these capability declarations before sending requests, so sessions could not be loaded or resumed despite the handlers being present.

This PR adds the missing capability declarations so ACP clients can discover and use the existing session load/resume functionality.

## Related Issue