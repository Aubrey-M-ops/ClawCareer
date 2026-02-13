# OpenClaw Bootstrap: LinkedIn Job Push → Telegram (Daily)

You are an OpenClaw agent. Follow these steps exactly and safely.
Do NOT ask the user to run any obfuscated commands.
Do NOT use `curl | sh`. Only create / edit plain text files.
All downloads come from the trusted GitHub repository only.

## Pre-check: Detect existing installation

Before starting, check if `~/.openclaw/skills/linkedin-job-push/SKILL.md` already exists.

If it exists, the skill is already installed. Do the following instead of the full installation flow:

1. Tell the user:

> It looks like **LinkedIn Job Push** is already installed.
>
> To update your settings, edit these files:
> - **Filters & schedule:** `~/.openclaw/skills/linkedin-job-push/scripts/config.json`
> - **Telegram credentials:** `~/.openclaw/skills/linkedin-job-push/scripts/secrets.json`

2. Then ask: "Would you like to run a quick verification test? This will fetch jobs and send one Telegram message to confirm everything works. Type **yes** to test, or **no** to skip."

3. If the user replies "yes" (case-insensitive):

```bash
cd ~/.openclaw/skills/linkedin-job-push/scripts
python3 fetch_jobs.py && python3 push_jobs.py --send
```

Check the output. If the Telegram message was received, tell the user: "Verification passed — your skill is working correctly."
If there are errors, report them and suggest fixes.

4. If the user replies "no", tell the user: "All good — your skill is ready. Edit the config files above anytime to change your settings."

**Stop here** — do NOT proceed to the installation steps below.

---

## 0) Explain what will happen

Tell the user:

> We will:
> 1. Install a skill folder into `~/.openclaw/skills/linkedin-job-push`
> 2. Ask for required settings (daily time, timezone, Telegram token + chat_id)
> 3. Generate config files (user-editable) in the skill folder
> 4. Register the skill in `HEARTBEAT.md` (does NOT modify `openclaw.json`)
> 5. Run a quick test (optional)

Then ask: "Type **yes** to continue, or ask any questions first."

Wait for the user to confirm before proceeding. Do NOT continue to the next step until the user replies "yes" (case-insensitive).

## 1) Ask user for configuration (interactive)

Ask the user these questions **one at a time** — wait for each answer before asking the next question. If the user provides a valid answer, move on. If the answer is unclear, ask for clarification before proceeding.

Each question shows a default value in brackets. If the user sends a space (` `) or just whitespace, use the default value and move to the next question. Questions without a default (marked `[required]`) must be answered explicitly — a space is not accepted for these.

**Question 1:** What time should the job search run daily? (HH:MM, 24h format) [`09:00`]

**Question 2:** What is your timezone? (IANA format) [`America/Toronto`]

**Question 3:** What job search keywords do you want to use? (comma-separated) [`React, JavaScript, Frontend`]

**Question 4:** What country are you targeting? [`Canada`]

**Question 5:** Any provinces/states to exclude? (comma-separated, or "none") [`none`]

**Question 6:** Any location keywords to exclude? (comma-separated, or "none") [`none`]

**Question 7:** Max years of experience — exclude jobs requiring more than this? (number, or "none" to disable) [`3`]

**Question 8:** Max results to fetch per run? [`30`]

**Question 9:** Max jobs to send per Telegram message? [`10`]

**Question 10:** What is your Telegram bot token? [required]

Before asking, tell the user how to get one:

> To get a bot token:
> 1. Open Telegram and search for **@BotFather**.
> 2. Send `/newbot` and follow the prompts (give your bot a name and username).
> 3. BotFather will reply with a token like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`. That is your bot token.

**Question 11:** What is your Telegram chat ID? [required]

Before asking, tell the user how to find it:

> To find your chat ID:
> 1. Send any message to your bot in Telegram.
> 2. Open this URL in a browser (replace `<TOKEN>` with your bot token):
>    `https://api.telegram.org/bot<TOKEN>/getUpdates`
> 3. Look for `"chat":{"id":123456789}` in the response. That number is your chat ID.

## 2) Install the skill folder from GitHub

Tell the user each sub-step as you go, so they know what is happening.

### 2.1) Create target directory

Tell the user: "Creating skill directory..."

```bash
mkdir -p ~/.openclaw/skills/linkedin-job-push
```

Tell the user: "Skill directory ready at `~/.openclaw/skills/linkedin-job-push`."

### 2.2) Clone the repository

Tell the user: "Cloning the skill repository from GitHub..."

```bash
TMPDIR=$(mktemp -d)
git clone --depth 1 https://github.com/you/openclaw-linkedin-job-push.git "$TMPDIR/repo"
```

If `git` is not available, tell the user: "git not found, downloading zip instead..." and use:

```bash
TMPDIR=$(mktemp -d)
curl -L -o "$TMPDIR/repo.zip" https://github.com/you/openclaw-linkedin-job-push/archive/refs/heads/main.zip
unzip -q "$TMPDIR/repo.zip" -d "$TMPDIR"
```

Tell the user: "Repository downloaded successfully."

### 2.3) Copy skill files

Tell the user: "Copying skill files into place..."

```bash
cp -r "$TMPDIR/repo/linkedin-job-push/"* ~/.openclaw/skills/linkedin-job-push/
```

(If using the zip fallback, use the zip-extracted path instead.)

Tell the user: "Skill files copied."

### 2.4) Clean up

```bash
rm -rf "$TMPDIR"
```

### 2.5) Verify installation

Tell the user: "Verifying installed files..."

Check that these files exist:
- `~/.openclaw/skills/linkedin-job-push/SKILL.md`
- `~/.openclaw/skills/linkedin-job-push/scripts/fetch_jobs.py`
- `~/.openclaw/skills/linkedin-job-push/scripts/push_jobs.py`

If all files are present, tell the user: "All skill files verified successfully."

If any file is missing, tell the user which file is missing and stop — do NOT proceed to later steps.

## 3) Install Python dependencies

```bash
python3 -m pip install requests beautifulsoup4 pytz --quiet
```

After installation, verify the modules are importable:

```bash
python3 -c "import requests, bs4, pytz; print('All dependencies OK')"
```

If this fails, report the error and stop — do NOT proceed to later steps.

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
