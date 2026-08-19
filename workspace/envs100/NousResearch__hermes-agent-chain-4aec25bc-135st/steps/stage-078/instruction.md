**fix(cron): handle whitespace-only responses**

Salvage of #28151 by @joe102084.

**What:** Cron jobs that returned whitespace-only final responses (`"   \n\t  "`) were delivered as blank messages and recorded as successful runs. The empty-response soft-failure guard checked `not final_response` (truthy) instead of `not final_response.strip()`.

**How:** Strip before both the delivery decision and the soft-failure marker so whitespace-only output is treated the same as empty output. Test added covering the regression.

Original PR: