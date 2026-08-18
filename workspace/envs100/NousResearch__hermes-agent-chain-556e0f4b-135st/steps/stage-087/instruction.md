**fix(api-server): harden jobs API — input limits, field whitelist, startup check, tests**

(jobs API endpoints). Five hardening improvements:

1. **Cron startup check** — module imported once at class load, all endpoints return 501 if unavailable (vs 500 per-request import error)
2. **Input limits** — name ≤ 200 chars, prompt ≤ 5000 chars, repeat must be positive int
3. **Update field whitelist** — only `name/schedule/prompt/deliver/skills/repeat/enabled` pass through to `update_job()`, preventing arbitrary key injection via raw body merge
4. **Deduplicated validation** — `_check_job_id()` and `_check_jobs_available()` helpers replace boilerplate
5. **32 new tests** — list, create (6 validation cases), get, update (whitelist enforcement), delete, pause, resume, run, auth required (5 cases), cron unavailable (7 cases)

114 total API server tests pass (72 existing + 32 new + 10 webhook).