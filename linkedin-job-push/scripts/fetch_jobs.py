#!/usr/bin/env python3
"""
Fetch LinkedIn job listings based on config filters.
Writes results to jobs.json in the same directory.

Usage:
  python3 fetch_jobs.py              # fetch immediately
  python3 fetch_jobs.py --heartbeat  # only fetch if current time matches schedule
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
from datetime import datetime
from pathlib import Path

import pytz
import requests
from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.json"
JOBS_OUTPUT_PATH = SCRIPT_DIR / "jobs.json"

LINKEDIN_JOBS_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# LinkedIn geoId mapping for common countries
COUNTRY_GEO_IDS = {
    "canada": "101174742",
    "united states": "103644278",
    "united kingdom": "101165590",
    "australia": "101452733",
    "germany": "101282230",
    "france": "105015875",
    "india": "102713980",
    "china": "102890883",
    "japan": "101355337",
    "singapore": "102454443",
}


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        print(f"Error: config.json not found at {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_search_url(keywords: list[str], country: str, start: int = 0) -> str:
    keyword_str = " OR ".join(keywords)
    geo_id = COUNTRY_GEO_IDS.get(country.lower(), "")

    params = {
        "keywords": keyword_str,
        "location": country,
        "start": str(start),
        "sortBy": "DD",  # sort by date
        "f_TPR": "r86400",  # past 24 hours
    }
    if geo_id:
        params["geoId"] = geo_id

    return f"{LINKEDIN_JOBS_URL}?{urllib.parse.urlencode(params)}"


def parse_job_card(card) -> dict | None:
    """Parse a single LinkedIn job card from the HTML."""
    title_el = card.find("h3", class_="base-search-card__title")
    company_el = card.find("h4", class_="base-search-card__subtitle")
    location_el = card.find("span", class_="job-search-card__location")
    link_el = card.find("a", class_="base-card__full-link")
    time_el = card.find("time")

    if not title_el or not link_el:
        return None

    job_url = link_el.get("href", "").split("?")[0]
    # Extract job ID from URL
    job_id = ""
    if "view/" in job_url:
        job_id = job_url.split("view/")[-1].rstrip("/")
    elif "-" in job_url:
        job_id = job_url.split("-")[-1].rstrip("/")

    return {
        "id": job_id,
        "title": title_el.get_text(strip=True),
        "company": company_el.get_text(strip=True) if company_el else "Unknown",
        "location": location_el.get_text(strip=True) if location_el else "Unknown",
        "url": job_url,
        "posted": time_el.get("datetime", "") if time_el else "",
    }


LINKEDIN_JOB_DETAIL_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"


def fetch_job_description(job_id: str) -> str:
    """Fetch the full description for a single job by ID."""
    url = LINKEDIN_JOB_DETAIL_URL.format(job_id=job_id)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  Warning: failed to fetch description for {job_id}: {e}", file=sys.stderr)
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")
    desc_el = soup.find("div", class_="description__text")
    if not desc_el:
        desc_el = soup.find("div", class_="show-more-less-html__markup")
    return desc_el.get_text(separator=" ", strip=True) if desc_el else ""


def fetch_jobs(config: dict) -> list[dict]:
    """Fetch job listings from LinkedIn based on config filters."""
    filters = config.get("filters", {})
    keywords = filters.get("keywords", [])
    country = filters.get("country", "Canada")
    max_results = filters.get("maxResults", 30)

    if not keywords:
        print("Error: no keywords configured in config.json", file=sys.stderr)
        sys.exit(1)

    all_jobs = []
    start = 0
    batch_size = 25  # LinkedIn returns ~25 per page

    print(f"Fetching jobs for: {', '.join(keywords)} in {country}")

    while len(all_jobs) < max_results:
        url = build_search_url(keywords, country, start)

        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Request error at start={start}: {e}", file=sys.stderr)
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("div", class_="base-card")

        if not cards:
            break

        for card in cards:
            job = parse_job_card(card)
            if job and job["id"]:
                all_jobs.append(job)

        print(f"  Fetched {len(cards)} cards (total so far: {len(all_jobs)})")

        if len(cards) < batch_size:
            break

        start += batch_size
        time.sleep(1.5)  # polite delay

    # Trim to max_results
    all_jobs = all_jobs[:max_results]

    # Fetch full description for each job
    print(f"Fetching descriptions for {len(all_jobs)} jobs...")
    for i, job in enumerate(all_jobs):
        job["description"] = fetch_job_description(job["id"])
        if job["description"]:
            print(f"  [{i+1}/{len(all_jobs)}] Got description for: {job['title'][:50]}")
        else:
            print(f"  [{i+1}/{len(all_jobs)}] No description for: {job['title'][:50]}")
        time.sleep(1)  # polite delay

    return all_jobs


def should_run_now(config: dict) -> bool:
    """Check if current time matches the configured schedule (within ±5 minutes)."""
    schedule = config.get("schedule", {})
    target_time = schedule.get("time", "")
    timezone_str = schedule.get("timezone", "America/Toronto")

    if not target_time:
        # No schedule configured — always run
        return True

    tz = pytz.timezone(timezone_str)
    now = datetime.now(tz)

    target_hour, target_min = map(int, target_time.split(":"))
    diff = abs(now.hour * 60 + now.minute - (target_hour * 60 + target_min))

    return diff <= 5


def main():
    parser = argparse.ArgumentParser(description="Fetch LinkedIn job listings")
    parser.add_argument(
        "--heartbeat",
        action="store_true",
        help="Only run if current time matches config schedule (±5 min)",
    )
    args = parser.parse_args()

    config = load_config()

    if args.heartbeat and not should_run_now(config):
        print("Not scheduled time. Exiting silently.")
        sys.exit(0)

    jobs = fetch_jobs(config)

    with open(JOBS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(jobs)} jobs to {JOBS_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
