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

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.json"
SECRETS_PATH = SCRIPT_DIR / "secrets.json"
JOBS_PATH = SCRIPT_DIR / "jobs.json"
STATE_PATH = SCRIPT_DIR / "state.json"

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


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


def filter_jobs(jobs: list[dict], config: dict) -> list[dict]:
    """Apply location-based exclusion filters."""
    filters = config.get("filters", {})
    exclude_provinces = [p.lower() for p in filters.get("excludeProvinces", [])]
    exclude_keywords = [k.lower() for k in filters.get("excludeLocationKeywords", [])]

    filtered = []
    for job in jobs:
        location = job.get("location", "").lower()

        # Check province codes
        excluded = False
        for prov in exclude_provinces:
            if prov in location:
                excluded = True
                break

        # Check location keywords
        if not excluded:
            for kw in exclude_keywords:
                if kw in location:
                    excluded = True
                    break

        if not excluded:
            filtered.append(job)

    return filtered


# Map English number words to integers
_WORD_TO_NUM = {
    "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
}

# Regex to extract years-of-experience mentions from job text
_EXPER_RE = re.compile(
    r"""(
        # "3 years" / "5+ years" / "8 yrs" / "7-10 years"
        \b(\d+)\s*(\+|plus)?\s*(?:years?|yrs?)\b
        |
        # "3-5 years" / "4 – 7 years"
        \b(\d+)\s*[-–]\s*(\d+)\s*(?:years?|yrs?)\b
        |
        # "minimum 3 years" / "at least 5 years"
        \b(?:minimum|min\.?|at\s*least|at\s*min\.?)\s*(\d+)\s*(?:years?|yrs?)\b
        |
        # English words: "three years" / "five+ years"
        \b(three|four|five|six|seven|eight|nine|ten|
           eleven|twelve|thirteen|fourteen|fifteen|
           sixteen|seventeen|eighteen|nineteen|twenty)
        \s*(\+|plus)?\s*(?:years?|yrs?)\b
    )""",
    re.IGNORECASE | re.VERBOSE,
)


def extract_min_experience_years(text: str) -> int | None:
    """Extract the minimum years of experience required from text.

    Returns the highest number found across all matches, or None if
    no experience requirement is mentioned.
    """
    if not text:
        return None

    max_years = None
    for m in _EXPER_RE.finditer(text):
        # "N years" or "N+ years"
        if m.group(2):
            years = int(m.group(2))
        # "N-M years" — take the upper bound (stricter: if range exceeds max, exclude)
        elif m.group(4) and m.group(5):
            years = int(m.group(5))
        # "minimum N years"
        elif m.group(6):
            years = int(m.group(6))
        # English word
        elif m.group(7):
            years = _WORD_TO_NUM.get(m.group(7).lower(), 0)
        else:
            continue

        if max_years is None or years > max_years:
            max_years = years

    return max_years


def filter_by_experience(jobs: list[dict], max_years: int | None) -> list[dict]:
    """Exclude jobs that require more than max_years of experience.

    Checks both job title and description. If max_years is None, no filtering.
    """
    if max_years is None:
        return jobs

    filtered = []
    for job in jobs:
        text = f"{job.get('title', '')} {job.get('description', '')}"
        required = extract_min_experience_years(text)
        if required is not None and required > max_years:
            print(f"  Excluded (requires {required}yr): {job['title'][:60]}")
            continue
        filtered.append(job)
    return filtered


def deduplicate(jobs: list[dict], state: dict) -> list[dict]:
    """Remove jobs that have already been sent."""
    seen = set(state.get("seen_job_ids", []))
    new_jobs = [j for j in jobs if j["id"] not in seen]
    return new_jobs


def format_telegram_message(jobs: list[dict], keyword_str: str) -> str:
    """Format jobs into a Telegram-friendly message (HTML parse mode)."""
    tz = pytz.timezone("America/Toronto")
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M %Z")
    lines = [
        f"<b>LinkedIn Jobs Daily Push</b>",
        f"<i>{now}</i>",
        f"Keywords: {keyword_str}",
        f"New jobs found: {len(jobs)}",
        "",
    ]

    for i, job in enumerate(jobs, 1):
        lines.append(
            f"{i}. <a href=\"{job['url']}\">{job['title']}</a>\n"
            f"   {job['company']} | {job['location']}"
        )
        if job.get("posted"):
            lines.append(f"   Posted: {job['posted']}")
        lines.append("")

    if not jobs:
        lines.append("No new jobs matching your filters today.")

    return "\n".join(lines)


def send_telegram(message: str, token: str, chat_id: str) -> bool:
    """Send a message via Telegram Bot API."""
    url = TELEGRAM_API.format(token=token)
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


def split_message(text: str, max_len: int = 4096) -> list[str]:
    """Split a long message into chunks that fit Telegram's limit."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    lines = text.split("\n")
    current = ""
    for line in lines:
        if len(current) + len(line) + 1 > max_len:
            chunks.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line
    if current:
        chunks.append(current)
    return chunks


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

    # Filter by location
    filtered = filter_jobs(jobs, config)
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
    max_send = config.get("filters", {}).get("maxSend", 10)
    to_send = new_jobs[:max_send]

    # Format message
    keywords = config.get("filters", {}).get("keywords", [])
    keyword_str = ", ".join(keywords)
    message = format_telegram_message(to_send, keyword_str)

    if args.dry_run:
        print("\n--- DRY RUN (message preview) ---\n")
        # Strip HTML tags for terminal display
        import re
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
