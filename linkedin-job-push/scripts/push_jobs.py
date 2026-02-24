#!/usr/bin/env python3
"""
Read jobs.json, apply filters, deduplicate against state.json,
and push new jobs to Telegram.

Usage:
  python3 push_jobs.py --send       # filter + dedup + send to Telegram
  python3 push_jobs.py --dry-run    # filter + dedup + print (no Telegram)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import pytz
import requests

from constants import TELEGRAM_SEND_MESSAGE_URL
from util.filter import deduplicate, filter_by_experience, filter_by_keywords, filter_by_location
from util.formatter import format_telegram_message, split_message

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.json"
SECRETS_PATH = SCRIPT_DIR / "secrets.json"
JOBS_PATH = SCRIPT_DIR / "jobs.json"
STATE_PATH = SCRIPT_DIR / "state.json"


def load_json(path: Path) -> dict | list:
    if not path.exists():
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def load_state() -> dict:
    if STATE_PATH.exists():
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"seen_job_ids": [], "last_run": None}


def load_secrets() -> dict:
    """Load Telegram credentials from secrets.json or environment variables."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

    if token and chat_id:
        return {"TELEGRAM_BOT_TOKEN": token, "TELEGRAM_CHAT_ID": chat_id}

    if SECRETS_PATH.exists():
        secrets = load_json(SECRETS_PATH)
        return {
            "TELEGRAM_BOT_TOKEN": secrets.get("TELEGRAM_BOT_TOKEN", ""),
            "TELEGRAM_CHAT_ID": secrets.get("TELEGRAM_CHAT_ID", ""),
        }

    print("Error: Telegram credentials not found in env or secrets.json", file=sys.stderr)
    sys.exit(1)


def send_telegram(message: str, token: str, chat_id: str) -> bool:
    """Send a message via Telegram Bot API."""
    url = TELEGRAM_SEND_MESSAGE_URL.format(token=token)
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        if result.get("ok"):
            print("Telegram message sent successfully.")
            return True
        else:
            print(f"Telegram API error: {result}", file=sys.stderr)
            return False
    except requests.RequestException as e:
        print(f"Telegram send failed: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Push LinkedIn jobs to Telegram")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--send", action="store_true", help="Send to Telegram")
    group.add_argument("--dry-run", action="store_true", help="Print only, no send")
    args = parser.parse_args()

    config = load_json(CONFIG_PATH)
    jobs = load_json(JOBS_PATH)
    state = load_state()

    filters = config.get("filters", {})

    # Filter by keywords
    filtered = filter_by_keywords(jobs, config)
    print(f"After keyword filter: {len(filtered)}/{len(jobs)} jobs remain")

    # Filter by location
    filtered = filter_by_location(filtered, config)
    print(f"After location filter: {len(filtered)}/{len(jobs)} jobs remain")

    # Filter by experience
    max_exp = filters.get("maxExperienceYears")
    filtered = filter_by_experience(filtered, max_exp)
    if max_exp is not None:
        print(f"After experience filter (≤{max_exp}yr): {len(filtered)} jobs remain")

    # Deduplicate
    new_jobs = deduplicate(filtered, state)
    print(f"After deduplication: {len(new_jobs)} new jobs")

    # Limit
    max_send = filters.get("maxSend", 10)
    print('maxSend >>>>> ', max_send)

    to_send = new_jobs[:max_send]

    # Format message
    keywords = filters.get("keywords", [])
    keyword_str = ", ".join(keywords)
    message = format_telegram_message(to_send, keyword_str)

    if args.dry_run:
        print("\n--- DRY RUN (message preview) ---\n")
        plain = re.sub(r"<[^>]+>", "", message)
        print(plain)
    elif args.send:
        secrets = load_secrets()
        token = secrets["TELEGRAM_BOT_TOKEN"]
        chat_id = secrets["TELEGRAM_CHAT_ID"]

        if not token or not chat_id:
            print("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is empty", file=sys.stderr)
            sys.exit(1)

        chunks = split_message(message)
        success = True
        for chunk in chunks:
            if not send_telegram(chunk, token, chat_id):
                success = False
                break

        if not success:
            sys.exit(1)

    # Update state with all new job IDs (even if we only sent a subset)
    seen = set(state.get("seen_job_ids", []))
    for job in new_jobs:
        seen.add(job["id"])
    state["seen_job_ids"] = list(seen)
    state["last_run"] = datetime.now(pytz.timezone("America/Toronto")).isoformat()
    save_state(state)
    print(f"State updated. Total seen jobs: {len(seen)}")


if __name__ == "__main__":
    main()
