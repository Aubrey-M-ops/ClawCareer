"""Message formatting utilities."""

from __future__ import annotations

from datetime import datetime

import pytz


def format_telegram_message(jobs: list[dict], keyword_str: str) -> str:
    """Format jobs into a Telegram-friendly message (HTML parse mode)."""
    tz = pytz.timezone("America/Toronto")
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M %Z")
    lines = [
        "<b>LinkedIn Jobs Daily Push</b>",
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
