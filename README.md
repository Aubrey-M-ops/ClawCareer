# 🦞 ClawCareer — LinkedIn Job Push → Telegram (OpenClaw Skill)

> **v1** — Currently supports **LinkedIn → Telegram** only. More job sources and notification channels planned for future versions.

ClawCareer is an OpenClaw skill that helps your AI agent monitor LinkedIn job listings and send filtered opportunities directly to your Telegram chat — hands-free, daily.

## Features

- **One-command install** — just give your OpenClaw agent the skill URL and it walks you through setup, one question at a time
- **LinkedIn public scraping** — no API key or LinkedIn account needed; fetches job cards + full descriptions from the guest endpoint
- **Smart filtering** — exclude by province/state, location keywords, and max years of experience (regex-based, supports ranges like "3-5 years" and words like "five years")
- **Telegram delivery** — sends formatted HTML job listings to your Telegram chat, auto-splits long messages to fit the 4096-char limit
- **Heartbeat-driven scheduling** — hooks into OpenClaw's heartbeat as a passive listener; the skill checks its own `config.json` schedule (±5 min window) and exits silently when it's not time, **does not modify `openclaw.json`**
- **Fully user-editable config** — all settings live in plain JSON files (`config.json` + `secrets.json`) that can be changed anytime without re-running the installer

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



## Configuration

### config.json

| Field | Description | Default |
|-------|-------------|---------|
| `schedule.time` | Daily trigger time (HH:MM, 24h format) | `09:00` |
| `schedule.timezone` | IANA timezone (e.g., `America/Toronto`) | `UTC` |
| `filters.keywords` | Job search keywords (array of strings) | — (required) |
| `filters.country` | Target country for job search | `Canada` |
| `filters.excludeProvinces` | Province/state codes to skip (e.g., `["QC", "AB"]`) | `[]` |
| `filters.excludeLocationKeywords` | Location keywords to skip (e.g., `["Quebec", "Montreal"]`) | `[]` |
| `filters.maxExperienceYears` | Exclude jobs requiring more than N years; omit or set `null` to disable | `3` |
| `filters.maxResults` | Max jobs to fetch per run | `30` |
| `filters.maxSend` | Max jobs to send per Telegram message | `10` |

### secrets.json

| Field | Description |
|-------|-------------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |

Alternatively, set these as environment variables.

## How It Triggers

This skill runs as a **hook on the OpenClaw runtime's heartbeat**. It does **not** have its own scheduler or cron job — instead, it piggybacks on the heartbeat that OpenClaw already runs at a regular interval (e.g., every 10 minutes).

Each time the heartbeat fires, it executes the commands listed in `~/.openclaw/HEARTBEAT.md`. This skill registers itself there, so the flow is:

1. OpenClaw heartbeat fires (e.g., every 10 min) → calls `fetch_jobs.py --heartbeat`
2. The script reads `schedule.time` and `schedule.timezone` from `config.json`
3. If the current time matches the configured schedule (within ±5 min), it fetches jobs and proceeds to send them
4. Otherwise it exits silently — zero side effects, zero network requests

This design means the skill does **not** modify `openclaw.json` or manage its own timer. It assumes heartbeat is already enabled by the user. The skill only controls **when** it actually does work, by comparing the current time against its own config.



## Compatibility

| Requirement | Version |
|-------------|---------|
| OpenClaw | >= 2026.2.x (with heartbeat support) |
| Python | >= 3.10 |
| Telegram Bot API |

## Security

- `secrets.json` is gitignored and should have `chmod 600`
- All code is auditable in this repo
- No remote script execution (`curl | sh` etc.)
- Only install from trusted sources

## License

MIT
