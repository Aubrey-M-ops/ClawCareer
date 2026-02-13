# OpenClaw Bootstrap: LinkedIn Job Push → Telegram (Daily)

You are an OpenClaw agent. Follow these steps exactly and safely.
Do NOT ask the user to run any obfuscated commands.
Do NOT use `curl | sh`. Only create / edit plain text files.
All downloads come from the trusted GitHub repository only.

## 0) Explain what will happen

Tell the user:

> We will:
> 1. Install a skill folder into `~/.openclaw/skills/linkedin-job-push`
> 2. Ask for required settings (daily time, timezone, Telegram token + chat_id)
> 3. Generate config files (user-editable) in the skill folder
> 4. Register the skill in `HEARTBEAT.md` (does NOT modify `openclaw.json`)
> 5. Run a quick test (optional)

## 1) Ask user for configuration (interactive)

Ask the user these questions in one message:

1. **Daily trigger time** (HH:MM, 24h format). Example: `09:00`
2. **Timezone** (IANA format). Example: `America/Toronto`
3. **Job search keywords** (comma-separated). Example: `React, JavaScript, Frontend`
4. **Target country**. Example: `Canada`
5. **Excluded provinces/states** (comma-separated, or "none"). Example: `QC, AB`
6. **Excluded location keywords** (comma-separated, or "none"). Example: `Quebec, Montreal, Alberta, Calgary`
7. **Max years of experience** (exclude jobs requiring more than this, or "none" to disable). Default: `3`
8. **Max results to fetch per run**. Default: `30`
9. **Max jobs to send per Telegram message**. Default: `10`
10. **Telegram bot token** (`TELEGRAM_BOT_TOKEN`)
11. **Telegram chat ID** (`TELEGRAM_CHAT_ID`)

If the user does not know their Telegram chat ID, tell them:

> 1. Send any message to your bot in Telegram.
> 2. Open this URL in a browser (replace `<TOKEN>` with your bot token):
>    `https://api.telegram.org/bot<TOKEN>/getUpdates`
> 3. Look for `"chat":{"id":123456789}` in the response. That number is your chat ID.

## 2) Install the skill folder from GitHub

Using the shell tool, execute:

```bash
# Create target directory
mkdir -p ~/.openclaw/skills/linkedin-job-push

# Clone the repo to a temp directory
TMPDIR=$(mktemp -d)
git clone --depth 1 https://github.com/you/openclaw-linkedin-job-push.git "$TMPDIR/repo"

# Copy only the inner skill folder
cp -r "$TMPDIR/repo/linkedin-job-push/"* ~/.openclaw/skills/linkedin-job-push/

# Clean up
rm -rf "$TMPDIR"
```

If `git` is not available, download and extract the zip instead:

```bash
TMPDIR=$(mktemp -d)
curl -L -o "$TMPDIR/repo.zip" https://github.com/you/openclaw-linkedin-job-push/archive/refs/heads/main.zip
unzip -q "$TMPDIR/repo.zip" -d "$TMPDIR"
cp -r "$TMPDIR/openclaw-linkedin-job-push-main/linkedin-job-push/"* ~/.openclaw/skills/linkedin-job-push/
rm -rf "$TMPDIR"
```

Verify these files exist:
- `~/.openclaw/skills/linkedin-job-push/SKILL.md`
- `~/.openclaw/skills/linkedin-job-push/scripts/fetch_jobs.py`
- `~/.openclaw/skills/linkedin-job-push/scripts/push_jobs.py`

If any file is missing, report the error and stop.

## 3) Install Python dependencies

```bash
pip3 install requests beautifulsoup4 pytz --quiet
```

## 4) Generate user-editable config files

### 4.1) config.json

Create `~/.openclaw/skills/linkedin-job-push/scripts/config.json` with the user's answers:

```json
{
  "schedule": {
    "time": "<USER_TIME>",
    "timezone": "<USER_TIMEZONE>"
  },
  "filters": {
    "keywords": ["<keyword1>", "<keyword2>"],
    "country": "<USER_COUNTRY>",
    "excludeProvinces": ["<prov1>", "<prov2>"],
    "excludeLocationKeywords": ["<kw1>", "<kw2>"],
    "maxExperienceYears": <USER_MAX_EXP_OR_OMIT>,
    "maxResults": <USER_MAX_RESULTS>,
    "maxSend": <USER_MAX_SEND>
  }
}
```

### 4.2) secrets.json

Create `~/.openclaw/skills/linkedin-job-push/scripts/secrets.json`:

```json
{
  "TELEGRAM_BOT_TOKEN": "<USER_TOKEN>",
  "TELEGRAM_CHAT_ID": "<USER_CHAT_ID>"
}
```

Then set restrictive permissions:

```bash
chmod 600 ~/.openclaw/skills/linkedin-job-push/scripts/secrets.json
```

### 4.3) Initialize state file

If `scripts/state.json` does not exist, create it:

```json
{
  "seen_job_ids": [],
  "last_run": null
}
```

## 5) Register skill in HEARTBEAT.md

> **Important:** Do NOT modify `~/.openclaw/openclaw.json`.
> The user's heartbeat cadence is their own — we only hook into it.
> Schedule logic lives entirely inside the skill's Python code.

### 5.1) Verify heartbeat is enabled

Check that `~/.openclaw/openclaw.json` exists and contains a `"heartbeat"` key.

- If yes: proceed. Do NOT change any of its values.
- If no: inform the user that OpenClaw heartbeat must be enabled for
  automatic daily runs. Show them how to enable it manually:

```
To enable heartbeat, add to ~/.openclaw/openclaw.json:
{
  "heartbeat": {
    "every": "10m"
  }
}
```

Do NOT write this file for the user automatically.

### 5.2) Create/update HEARTBEAT.md

Create `~/.openclaw/HEARTBEAT.md` (or append if it already exists —
do not overwrite other skills' sections):

```md
## LinkedIn Job Push

This heartbeat runs periodically.

Run the LinkedIn Job Push skill:
1. Execute: `python3 ~/.openclaw/skills/linkedin-job-push/scripts/fetch_jobs.py --heartbeat`
2. Then:    `python3 ~/.openclaw/skills/linkedin-job-push/scripts/push_jobs.py --send`

The skill reads its own schedule from
`~/.openclaw/skills/linkedin-job-push/scripts/config.json`
and decides internally whether it is time to run. If not, it exits silently.
```

## 6) Smoke test (optional but recommended)

Ask the user:

> Do you want to run a quick test now? This will fetch jobs and send a test message to your Telegram.

If yes:

```bash
cd ~/.openclaw/skills/linkedin-job-push/scripts
python3 fetch_jobs.py
python3 push_jobs.py --send
```

Check for errors. If Telegram message was received, confirm success.

## 8) Print final summary

Show the user:

```
Installation complete!

Config files (editable):
  ~/.openclaw/skills/linkedin-job-push/scripts/config.json
  ~/.openclaw/skills/linkedin-job-push/scripts/secrets.json  (chmod 600)

Daily schedule: <TIME> <TIMEZONE>
(The skill checks its own schedule — openclaw.json was NOT modified)

To change schedule:
  Edit config.json → "schedule.time" and "schedule.timezone"

To run manually (skips schedule check):
  cd ~/.openclaw/skills/linkedin-job-push/scripts
  python3 fetch_jobs.py && python3 push_jobs.py --send

To update keywords/filters:
  Edit ~/.openclaw/skills/linkedin-job-push/scripts/config.json
```
