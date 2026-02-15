## LinkedIn Job Push (daily)
If due for a LinkedIn Job Push check (based on `lastCheck` in `memory/linkedin-job-push-state.json`):
1. Execute: `python3 ~/.openclaw/skills/linkedin-job-push/scripts/fetch_jobs.py --heartbeat`
2. Then:    `python3 ~/.openclaw/skills/linkedin-job-push/scripts/push_jobs.py --send`
3. Update `lastCheck` in `memory/linkedin-job-push-state.json` to the current ISO 8601 timestamp

The skill reads its own schedule from `config.json` and decides internally whether it is time to run. If not, it exits silently.
