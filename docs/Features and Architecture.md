# Features

- **One-command install** — just give your OpenClaw agent the skill URL and it walks you through setup, one question at a time
- **LinkedIn public scraping** — no API key or LinkedIn account needed; fetches job cards + full descriptions from the guest endpoint
- **Smart filtering** — exclude by province/state, location keywords, and max years of experience (regex-based, supports ranges like "3-5 years" and words like "five years")
- **Telegram delivery** — sends formatted HTML job listings to your Telegram chat, auto-splits long messages to fit the 4096-char limit
- **Heartbeat-driven scheduling** — integrates with OpenClaw's heartbeat using memory-based state tracking; the skill checks `memory/linkedin-job-push-state.json` to track last check time and exits silently when it's not due, **does not modify `openclaw.json`**
- **Fully user-editable config** — all settings live in plain JSON files (`config.json` + `secrets.json`) that can be changed anytime without re-running the installer

# How It Triggers

This skill runs as a **hook on the OpenClaw runtime's heartbeat**. It does **not** have its own scheduler or cron job — instead, it piggybacks on the heartbeat that OpenClaw already runs at a regular interval (e.g., every 10 minutes).

## Memory-Based State Tracking

The skill uses **memory-based state tracking** to determine when to run:

1. **State file**: `memory/linkedin-job-push-state.json` stores:
   - `lastCheck`: ISO 8601 timestamp of the last execution
   - `schedule`: User's configured daily time and timezone
   - `keywords`: Job search keywords for reference

2. **Heartbeat integration**: Add the skill to your heartbeat file (see `docs/HEARTBEAT.md` for template):
   ```markdown
   ## LinkedIn Job Push (daily)
   If due for a LinkedIn Job Push check (based on `lastCheck` in `memory/linkedin-job-push-state.json`):
   1. Execute: `python3 ~/.openclaw/skills/linkedin-job-push/scripts/fetch_jobs.py --heartbeat`
   2. Then:    `python3 ~/.openclaw/skills/linkedin-job-push/scripts/push_jobs.py --send`
   3. Update `lastCheck` in `memory/linkedin-job-push-state.json` to the current ISO 8601 timestamp
   ```

3. **Execution flow**:
   - OpenClaw heartbeat fires (e.g., every 10 min) → calls `fetch_jobs.py --heartbeat`
   - The script reads `schedule.time` and `schedule.timezone` from `config.json`
   - Checks `lastCheck` in `memory/linkedin-job-push-state.json`
   - If current time matches the configured schedule (within ±5 min) and sufficient time has passed since last check, it fetches jobs
   - Updates `lastCheck` timestamp after successful execution
   - Otherwise exits silently — zero side effects, zero network requests

## Note on HEARTBEAT.md

- **`docs/HEARTBEAT.md`** is a **documentation template** showing how to integrate the skill into your heartbeat workflow
- The skill does **not** create or modify a central `~/.openclaw/HEARTBEAT.md` file
- Users integrate the skill by adding the documented commands to their own heartbeat system
- This design means the skill does **not** modify `openclaw.json` or manage its own timer — it only controls **when** it actually does work based on memory state and config
