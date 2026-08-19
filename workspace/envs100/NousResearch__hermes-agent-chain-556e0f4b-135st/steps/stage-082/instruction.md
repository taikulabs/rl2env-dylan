**fix(cron): silent jobs return empty response for delivery skip**

## Summary

Silent cron jobs that complete work via tools but produce no final text response were delivering `(No response generated)` instead of staying silent. The placeholder string overwrote `final_response`, making `bool(deliver_content)` always True.

**Fix:** Separate the log placeholder from the delivery value. `final_response` stays empty for delivery logic; `logged_response` gets the placeholder for the output log.
