"""Job filtering and deduplication logic."""

from __future__ import annotations

import re

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
        if m.group(2):
            years = int(m.group(2))
        elif m.group(4) and m.group(5):
            years = int(m.group(5))
        elif m.group(6):
            years = int(m.group(6))
        elif m.group(7):
            years = _WORD_TO_NUM.get(m.group(7).lower(), 0)
        else:
            continue

        if max_years is None or years > max_years:
            max_years = years

    return max_years


def filter_by_keywords(jobs: list[dict], config: dict) -> list[dict]:
    """Keep only jobs whose title or description contains at least one keyword."""
    keywords = [k.lower() for k in config.get("filters", {}).get("keywords", [])]
    if not keywords:
        return jobs

    filtered = []
    for job in jobs:
        text = f"{job.get('title', '')} {job.get('description', '')}".lower()
        if any(kw in text for kw in keywords):
            filtered.append(job)
    return filtered


def filter_by_location(jobs: list[dict], config: dict) -> list[dict]:
    """Apply location-based exclusion filters."""
    filters = config.get("filters", {})
    exclude_provinces = [p.lower() for p in filters.get("excludeProvinces", [])]
    exclude_keywords = [k.lower() for k in filters.get("excludeLocationKeywords", [])]

    filtered = []
    for job in jobs:
        location = job.get("location", "").lower()

        excluded = False
        for prov in exclude_provinces:
            if prov in location:
                excluded = True
                break

        if not excluded:
            for kw in exclude_keywords:
                if kw in location:
                    excluded = True
                    break

        if not excluded:
            filtered.append(job)

    return filtered


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
    return [j for j in jobs if j["id"] not in seen]
