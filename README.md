# LinkedIn Job Push → Telegram (OpenClaw Skill)

> **v1** — Currently supports **LinkedIn → Telegram** only. More job sources and notification channels planned for future versions.

Automatically fetch LinkedIn job listings daily and push them to your Telegram chat via an OpenClaw skill.

## Features

- Scrapes LinkedIn public job search (no API key needed)
- Fetches full job descriptions for accurate filtering
- Filters by location (exclude provinces/keywords)
- Filters by experience requirements (e.g., skip jobs asking for 5+ years)
- Deduplicates across runs (never sends the same job twice)
- Schedule-aware heartbeat: skill checks its own schedule internally, **does not modify `openclaw.json`**

## Quick Start (One Command)

Tell your OpenClaw agent:

```
Read https://github.com/Aubrey-M-ops/ClawCareer/skill.md
```

The agent will guide you through:
1. Installing the skill
2. Configuring your job search filters
3. Setting up Telegram credentials
4. Registering the skill in `HEARTBEAT.md`

## Project Structure

```
BOOTSTRAP.md                  # One-click install script (Read this URL)

linkedin-job-push/            # The actual OpenClaw skill
  SKILL.md                    # Skill description
  scripts/
    fetch_jobs.py             # Scrapes LinkedIn job cards + descriptions
    push_jobs.py              # Filters, deduplicates, sends to Telegram
    config.json.example       # Template config
    config.schema.json        # JSON Schema for config validation
    state.json.example        # Template state file

docs/
  Mannual Installation.md     # Step-by-step manual setup guide
```

## Configuration

### config.json

| Field | Description |
|-------|-------------|
| `schedule.time` | Daily trigger time (HH:MM, 24h) |
| `schedule.timezone` | IANA timezone |
| `filters.keywords` | Job search keywords |
| `filters.country` | Target country |
| `filters.excludeProvinces` | Province/state codes to skip |
| `filters.excludeLocationKeywords` | Location keywords to skip |
| `filters.maxExperienceYears` | Exclude jobs requiring more than N years (omit to disable) |
| `filters.maxResults` | Max jobs to fetch per run (default: 30) |
| `filters.maxSend` | Max jobs per Telegram message (default: 10) |

### secrets.json

| Field | Description |
|-------|-------------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |

Alternatively, set these as environment variables.

## Daily Automation

This skill does **not** modify `openclaw.json`. It assumes heartbeat is already enabled by the user. The skill controls its own schedule internally:

1. Heartbeat periodically calls `fetch_jobs.py --heartbeat`
2. The script reads `schedule.time` and `schedule.timezone` from `config.json`
3. If current time matches (within ±5 min), it fetches jobs and continues
4. Otherwise it exits silently — zero side effects

## Security

- `secrets.json` is gitignored and should have `chmod 600`
- All code is auditable in this repo
- No remote script execution (`curl | sh` etc.)
- Only install from trusted sources

## License

MIT
