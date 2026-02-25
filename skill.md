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

2. Ask: "Would you like to **reinstall** it from scratch? This will overwrite the current installation. Type **yes** to reinstall, or **no** to keep the current setup."

3. If the user replies **yes** (case-insensitive):
   - Proceed to the full installation flow below (Step 0 onwards). The existing files will be overwritten.

4. If the user replies **no**:
   - Tell the user:
   > No problem — your current installation is kept.
   >
   > To update your settings, edit these files:
   > - **Filters & schedule:** `~/.openclaw/skills/linkedin-job-push/scripts/config.json`
   > - **Telegram credentials:** `~/.openclaw/skills/linkedin-job-push/scripts/secrets.json`
   >
   > To run a quick verification test:
   > ```
   > cd ~/.openclaw/skills/linkedin-job-push/scripts
   > python3 fetch_jobs.py && python3 push_jobs.py --send
   > ```

   **Stop here** — do NOT proceed to the installation steps below.

---

## 0) Explain what will happen — then proceed immediately

Tell the user:

> We will:
> 1. Install a skill folder into `~/.openclaw/skills/linkedin-job-push`
> 2. Ask for required settings (daily time, timezone, Telegram token + chat_id)
> 3. Generate config files (user-editable) in the skill folder
> 4. Register the skill's `HEARTBEAT.md` inside the skill directory (does NOT modify `openclaw.json`)
> 5. Run a quick test (optional)

Do NOT ask for confirmation. Proceed directly to Step 1 after showing this summary.

## 1) Ask user for configuration (interactive)

Ask the user these questions **one at a time** — wait for each answer before asking the next question. If the user provides a valid answer, move on. If the answer is unclear, ask for clarification before proceeding.

Each question shows a default value in brackets. To use the default, the user should copy and send the default value shown. Questions without a default (marked `[required]`) must be answered explicitly.

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
git clone --depth 1 https://github.com/Aubrey-M-ops/ClawCareer.git "$TMPDIR/repo"
```

If `git` is not available, tell the user: "git not found, downloading zip instead..." and use:

```bash
TMPDIR=$(mktemp -d)
curl -L -o "$TMPDIR/repo.zip" https://github.com/Aubrey-M-ops/ClawCareer/archive/refs/heads/main.zip
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

## 5) Register heartbeat and memory tracking

> **Important:** Do NOT modify `~/.openclaw/openclaw.json`.
> The user's heartbeat cadence is their own — we only hook into it.
> Schedule logic lives entirely inside the skill's Python code.

### Step 1: Add to your heartbeat file

Add this to your `HEARTBEAT.md` (or equivalent periodic task list):

```markdown
## LinkedIn Job Push (daily)
This heartbeat runs periodically.

Run the LinkedIn Job Push skill:

1. Execute: `python3 ~/.openclaw/skills/linkedin-job-push/scripts/fetch_jobs.py --heartbeat`
2. **Only if** the fetch script actually ran (didn't exit with "Not scheduled time"), then run:
   `python3 ~/.openclaw/skills/linkedin-job-push/scripts/push_jobs.py --send`
3. **Always** (regardless of whether the script ran): update `lastCheck` in `memory/linkedin-job-push-state.json` to the current timestamp.

> ⏳ **Note:** `fetch_jobs.py` fetches full job descriptions one by one with rate-limit delays.
> For 30 jobs this takes roughly **1–3 minutes**. Do not interrupt — progress is printed to terminal.

The skill reads its own schedule from
`~/.openclaw/skills/linkedin-job-push/scripts/config.json`
and decides internally whether it is time to run. If the fetch exits silently, skip the push step
```

The skill reads its own schedule from `config.json` and decides internally whether it is time to run. If not, it exits silently.

### Step 2: Track when you last checked

Create or update your state in memory (e.g. `memory/linkedin-job-push-state.json`):

```json
{
  "lastCheck": null,
  "schedule": "<USER_TIME> <USER_TIMEZONE>",
  "keywords": ["<keyword1>", "<keyword2>"]
}
```

Update the `lastCheck` timestamp each time you check. This prevents over-checking.

## 6) Smoke test (optional but recommended)

Ask the user:

> Do you want to run a quick test now? This will fetch jobs and send a test message to your Telegram.

If yes, **first warn the user:**

> ⏳ **Heads up — this will take 1–3 minutes.**
> The script fetches up to `maxResults` jobs, then retrieves the full description for each one individually (with a short delay between requests to avoid being rate-limited by LinkedIn). For 30 jobs, expect roughly 90–120 seconds total.
> You'll see live progress in the terminal.

Then run:

```bash
cd ~/.openclaw/skills/linkedin-job-push/scripts
python3 fetch_jobs.py
python3 push_jobs.py --send
```

Check for errors. If Telegram message was received, confirm success.

## 7) Print final summary

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
  (⏳ expect 1–3 min depending on maxResults — progress is shown in terminal)

To update keywords/filters:
  Edit ~/.openclaw/skills/linkedin-job-push/scripts/config.json
```

---

## Updating

If the user wants to update an existing installation to the latest version, follow these steps.

### Pre-check: Verify existing installation

First, check if `~/.openclaw/skills/linkedin-job-push/SKILL.md` exists.

- If it does NOT exist, tell the user: "LinkedIn Job Push is not installed yet. Would you like to install it?" and stop here.
- If it exists, proceed with the update flow below.

### Step 1: Backup existing configuration

Tell the user: "Backing up your configuration files..."

```bash
cd ~/.openclaw/skills/linkedin-job-push/scripts
cp config.json config.json.backup
cp secrets.json secrets.json.backup
cp state.json state.json.backup 2>/dev/null || true
```

Tell the user: "Configuration backed up successfully."

### Step 2: Download latest code

Tell the user: "Downloading latest version from GitHub..."

**If git is available:**

```bash
TMPDIR=$(mktemp -d)
git clone --depth 1 https://github.com/Aubrey-M-ops/ClawCareer.git "$TMPDIR/repo"
```

**If git is NOT available:**

```bash
TMPDIR=$(mktemp -d)
curl -L -o "$TMPDIR/repo.zip" https://github.com/Aubrey-M-ops/ClawCareer/archive/refs/heads/main.zip
unzip -q "$TMPDIR/repo.zip" -d "$TMPDIR"
# For non-git version, the path is "$TMPDIR/ClawCareer-main" instead of "$TMPDIR/repo"
```

Tell the user: "Latest code downloaded."

### Step 3: Update script files (preserving configuration)

Tell the user: "Updating script files (your config will be preserved)..."

**For git version:**

```bash
cp "$TMPDIR/repo/linkedin-job-push/scripts/fetch_jobs.py" ~/.openclaw/skills/linkedin-job-push/scripts/
cp "$TMPDIR/repo/linkedin-job-push/scripts/push_jobs.py" ~/.openclaw/skills/linkedin-job-push/scripts/
cp "$TMPDIR/repo/linkedin-job-push/scripts/constants.py" ~/.openclaw/skills/linkedin-job-push/scripts/
cp -r "$TMPDIR/repo/linkedin-job-push/scripts/util" ~/.openclaw/skills/linkedin-job-push/scripts/
```

**For non-git version, replace `$TMPDIR/repo` with `$TMPDIR/ClawCareer-main`**

Tell the user: "Scripts updated."

### Step 4: Update documentation

Tell the user: "Updating documentation files..."

```bash
cp "$TMPDIR/repo/linkedin-job-push/SKILL.md" ~/.openclaw/skills/linkedin-job-push/
cp "$TMPDIR/repo/linkedin-job-push/HEARTBEAT.md" ~/.openclaw/skills/linkedin-job-push/ 2>/dev/null || true
```

*For non-git version, replace `$TMPDIR/repo` with `$TMPDIR/ClawCareer-main`*

Tell the user: "Documentation updated."

### Step 5: Re-register heartbeat and update memory tracking

Tell the user: "Updating heartbeat instructions and memory state..."

Open your `HEARTBEAT.md` and replace the existing `## LinkedIn Job Push (daily)` section with:

```markdown
## LinkedIn Job Push (daily)
This heartbeat runs periodically.

Run the LinkedIn Job Push skill:

1. Execute: `python3 ~/.openclaw/skills/linkedin-job-push/scripts/fetch_jobs.py --heartbeat`
2. **Only if** the fetch script actually ran (didn't exit with "Not scheduled time"), then run:
   `python3 ~/.openclaw/skills/linkedin-job-push/scripts/push_jobs.py --send`
3. **Always** (regardless of whether the script ran): update `lastCheck` in `memory/linkedin-job-push-state.json` to the current timestamp.

> ⏳ **Note:** `fetch_jobs.py` fetches full job descriptions one by one with rate-limit delays.
> For 30 jobs this takes roughly **1–3 minutes**. Do not interrupt — progress is printed to terminal.

The skill reads its own schedule from
`~/.openclaw/skills/linkedin-job-push/scripts/config.json`
and decides internally whether it is time to run. If the fetch exits silently, skip the push step
```

Then ensure `memory/linkedin-job-push-state.json` exists and has the `lastCheck` field:

```json
{
  "lastCheck": null,
  "schedule": "<TIME> <TIMEZONE>",
  "keywords": ["<keyword1>", "<keyword2>"]
}
```

If the file already exists, preserve the existing `lastCheck` value — only add the field if it is missing.

Tell the user: "Heartbeat and memory tracking updated."

### Step 7: Clean up

```bash
rm -rf "$TMPDIR"
```

Tell the user: "Temporary files cleaned up."

### Step 8: Verify update

Tell the user: "Verifying the update..."

```bash
cd ~/.openclaw/skills/linkedin-job-push/scripts
python3 fetch_jobs.py
python3 push_jobs.py --dry-run
```

If this runs successfully and shows job listings, tell the user:

```
✅ Update complete!

Your configuration files were preserved:
  - config.json (your filters and schedule)
  - secrets.json (your Telegram credentials)
  - state.json (previously seen jobs)

Backup files created (just in case):
  - config.json.backup
  - secrets.json.backup
  - state.json.backup

To remove backups:
  cd ~/.openclaw/skills/linkedin-job-push/scripts
  rm -f *.backup
```

If the verification fails, tell the user about the error and suggest restoring from backup:

```bash
cd ~/.openclaw/skills/linkedin-job-push/scripts
mv config.json.backup config.json
mv secrets.json.backup secrets.json
mv state.json.backup state.json
```
