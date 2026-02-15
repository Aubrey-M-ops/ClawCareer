## Manual Installation

### Prerequisites

- Python 3.8+
- `pip3 install requests beautifulsoup4`
- A Telegram bot token (create via [@BotFather](https://t.me/BotFather))
- Your Telegram chat ID

### Setup

```bash
# Clone this repo
git clone https://github.com/Aubrey-M-ops/ClawCareer.git
cd ClawCareer

# Copy the skill to OpenClaw
mkdir -p ~/.openclaw/skills/linkedin-job-push
cp -r linkedin-job-push/* ~/.openclaw/skills/linkedin-job-push/

# Create config from template
cd ~/.openclaw/skills/linkedin-job-push/scripts
cp config.json.example config.json
cp state.json.example state.json

# Create secrets file
cat > secrets.json << 'EOF'
{
  "TELEGRAM_BOT_TOKEN": "your-token-here",
  "TELEGRAM_CHAT_ID": "your-chat-id-here"
}
EOF
chmod 600 secrets.json

# Edit config.json with your preferences
# Then test:
python3 fetch_jobs.py
python3 push_jobs.py --dry-run   # preview without sending
python3 push_jobs.py --send      # send to Telegram
```