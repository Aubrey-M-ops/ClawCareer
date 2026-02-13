# LinkedIn Job Push → Telegram (OpenClaw Skill)

Automatically fetch LinkedIn job listings daily and push them to your Telegram chat via an OpenClaw skill.

## Quick Start (One Command)

Tell your OpenClaw agent:

```
Read https://raw.githubusercontent.com/you/openclaw-linkedin-job-push/main/bootstrap/skill.md
```

The agent will guide you through:
1. Installing the skill
2. Configuring your job search filters
3. Setting up Telegram credentials
4. Enabling daily heartbeat trigger



## Project Structure

```
bootstrap/
  skill.md                    # One-click install script (Read this URL)

linkedin-job-push/            # The actual OpenClaw skill
  SKILL.md                    # Skill description
  scripts/
    fetch_jobs.py             # Scrapes LinkedIn public job search
    push_jobs.py              # Filters, deduplicates, sends to Telegram
    config.json.example       # Template config
    config.schema.json        # JSON Schema for config validation
    state.json.example        # Template state file
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
| `filters.maxResults` | Max jobs to fetch per run |
| `filters.maxSend` | Max jobs per Telegram message |

### secrets.json

| Field | Description |
|-------|-------------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |

Alternatively, set these as environment variables.

## Daily Automation

The bootstrap script configures OpenClaw heartbeat with a narrow `activeHours` window so the skill runs once daily at your chosen time. The heartbeat config lives in `~/.openclaw/openclaw.json`.

## Security

- `secrets.json` is gitignored and should have `chmod 600`
- All code is auditable in this repo
- No remote script execution (`curl | sh` etc.)
- Only install from trusted sources

## License

MIT
