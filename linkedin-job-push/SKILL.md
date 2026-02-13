# LinkedIn Job Push → Telegram

This skill fetches LinkedIn job listings based on your configured keywords and filters,
then sends the top results to your Telegram chat — daily, automatically.

## What this skill does

1. **Fetch**: Scrapes LinkedIn's public job search pages for listings matching your keywords and country, including full job descriptions.
2. **Filter**: Excludes jobs by location and by experience requirements (e.g., skip jobs asking for 5+ years when you set max 3).
3. **Deduplicate**: Tracks previously seen job IDs in `state.json` so you never get repeats.
4. **Push**: Sends a formatted summary of new jobs to your Telegram bot.

## Files

| File | Purpose |
|------|---------|
| `scripts/fetch_jobs.py` | Fetches job cards + descriptions from LinkedIn, writes `jobs.json`. Supports `--heartbeat` flag |
| `scripts/push_jobs.py`  | Reads `jobs.json`, filters (location + experience), deduplicates, sends to Telegram |
| `scripts/config.json`   | User-editable filters and schedule settings |
| `scripts/secrets.json`  | Telegram credentials (chmod 600) |
| `scripts/state.json`    | Persistent state: seen job IDs and last run time |

## Usage

### Manual run

```bash
cd ~/.openclaw/skills/linkedin-job-push/scripts
python3 fetch_jobs.py
python3 push_jobs.py --send
```

### Dry run (no Telegram, just print)

```bash
python3 push_jobs.py --dry-run
```

### Automatic daily run (via heartbeat)

This skill does **not** modify `openclaw.json`. It assumes heartbeat is already
enabled by the user. The skill controls its own schedule internally:

1. Heartbeat periodically calls `fetch_jobs.py --heartbeat`
2. The script reads `schedule.time` and `schedule.timezone` from `config.json`
3. If current time matches (within ±5 min), it fetches jobs and continues
4. Otherwise it exits silently — zero side effects

## Configuration

Edit `scripts/config.json`:

```json
{
  "schedule": { "time": "09:00", "timezone": "America/Toronto" },
  "filters": {
    "keywords": ["React", "JavaScript"],
    "country": "Canada",
    "excludeProvinces": ["QC", "AB"],
    "excludeLocationKeywords": ["Quebec", "Montreal"],
    "maxExperienceYears": 3,
    "maxResults": 30,
    "maxSend": 10
  }
}
```

## Dependencies

- Python 3.8+
- `requests`
- `beautifulsoup4`
- `pytz`

Install: `pip3 install requests beautifulsoup4 pytz`
