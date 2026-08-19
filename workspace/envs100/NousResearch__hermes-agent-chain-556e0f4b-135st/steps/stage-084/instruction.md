**fix(cron): scale missed-job grace window with schedule frequency**



Replaces hardcoded 120s grace window with dynamic scaling: min(period/2, 2h), floored at 120s. Daily jobs get 2h grace, hourly gets 30m, 5-min gets 2.5m. Prevents silent job skips on brief gateway reconnects.

41 cron/jobs tests pass.
