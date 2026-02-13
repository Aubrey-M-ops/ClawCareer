# Features

- **One-command install** — just give your OpenClaw agent the skill URL and it walks you through setup, one question at a time
- **LinkedIn public scraping** — no API key or LinkedIn account needed; fetches job cards + full descriptions from the guest endpoint
- **Smart filtering** — exclude by province/state, location keywords, and max years of experience (regex-based, supports ranges like "3-5 years" and words like "five years")
- **Telegram delivery** — sends formatted HTML job listings to your Telegram chat, auto-splits long messages to fit the 4096-char limit
- **Heartbeat-driven scheduling** — hooks into OpenClaw's heartbeat as a passive listener; the skill checks its own `config.json` schedule (±5 min window) and exits silently when it's not time, **does not modify `openclaw.json`**
- **Fully user-editable config** — all settings live in plain JSON files (`config.json` + `secrets.json`) that can be changed anytime without re-running the installer

# How It Triggers

This skill runs as a **hook on the OpenClaw runtime's heartbeat**. It does **not** have its own scheduler or cron job — instead, it piggybacks on the heartbeat that OpenClaw already runs at a regular interval (e.g., every 10 minutes).

Each time the heartbeat fires, it executes the commands listed in `~/.openclaw/HEARTBEAT.md`. This skill registers itself there, so the flow is:

1. OpenClaw heartbeat fires (e.g., every 10 min) → calls `fetch_jobs.py --heartbeat`
2. The script reads `schedule.time` and `schedule.timezone` from `config.json`
3. If the current time matches the configured schedule (within ±5 min), it fetches jobs and proceeds to send them
4. Otherwise it exits silently — zero side effects, zero network requests

This design means the skill does **not** modify `openclaw.json` or manage its own timer. It assumes heartbeat is already enabled by the user. The skill only controls **when** it actually does work, by comparing the current time against its own config.
