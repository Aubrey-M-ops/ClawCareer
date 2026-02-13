# 🦞 ClawCareer — LinkedIn Job Push → Telegram (OpenClaw Skill)

> **v1** — Currently supports **LinkedIn → Telegram** only. More job sources and notification channels planned for future versions.

✨ ClawCareer is an OpenClaw skill that helps your AI agent monitor LinkedIn job listings and send filtered opportunities directly to your Telegram chat — hands-free, daily.

## Quick Start (One Command)

Tell your OpenClaw agent:

```
Read https://github.com/Aubrey-M-ops/ClawCareer/skill.md
```

✅ That's it! The agent will guide you through:
1. Installing the skill
2. Configuring your job search filters
3. Setting up Telegram credentials
4. Registering the skill in `HEARTBEAT.md`

## Configuration

### `config.json`

| Field                              | Description                                                          | Default      |
| ---------------------------------- | -------------------------------------------------------------------- | ------------ |
| `schedule.time` | Daily trigger time (HH:MM, 24h format) | `09:00` |
| `schedule.timezone` | IANA timezone (e.g., `America/Toronto`) | `UTC` |
| `filters.keywords` | Job search keywords (array of strings) | — (required) |
| `filters.country` | Target country for job search | `Canada` |
| `filters.excludeProvinces` | Province/state codes to skip (e.g., `["QC", "AB"]`) | `[]` |
| `filters.excludeLocationKeywords` | Location keywords to skip (e.g., `["Quebec", "Montreal"]`) | `[]` |
| `filters.maxExperienceYears` | Exclude jobs requiring more than N years; omit or set `null` to disable | `3` |
| `filters.maxResults` | Max jobs to fetch per run | `30` |
| `filters.maxSend` | Max jobs to send per Telegram message | `10` |

### `secrets.json`

| Field                | Description                |
| -------------------- | -------------------------- |
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |

Alternatively, set these as environment variables.

For detailed features and how the heartbeat trigger works, see [Features and Architecture](docs/Features%20and%20Architecture.md).

## Compatibility

| Requirement       | Version                            |
| ----------------- | ---------------------------------- |
| OpenClaw | >= 2026.2.x (with heartbeat support) |
| Python | >= 3.10 |
| Telegram Bot API | — |

## Security

- `secrets.json` is gitignored and should have `chmod 600` (Your keys are stored in here.)

## License

MIT
