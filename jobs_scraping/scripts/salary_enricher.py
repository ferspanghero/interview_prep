"""Scraper-agnostic salary enrichment.

Receives job dicts with descriptions, extracts salary via regex, returns
enriched jobs. Any scraper can use this — it has no dependency on jobspy
or any specific data source.

Falls back to fetching the job URL directly when no description is available.
"""

import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

log = logging.getLogger(__name__)

SALARY_PATTERNS = [
    # "CA$125,000 to CA$150,000" or "CA$255.6K – CA$300.3K"
    r'C(?:A)?\$[\d,.]+[kK]?\s*(?:[-–—]|to)\s*C(?:A)?\$[\d,.]+[kK]?',
    # "C$180,000-$C260,000" (reversed $C on second value)
    r'C\$[\d,.]+[kK]?\s*[-–—]\s*\$C[\d,.]+[kK]?',
    # "CAD $114,400 - CAD $203,900" or "CAD $225,000 and CAD $255,000" or "CAD149,600 - CAD202,000"
    r'CAD\s*\$?[\d,.]+[kK]?\s*(?:[-–—]|and|to)\s*(?:CAD\s*\$?)?[\d,.]+[kK]?(?:\s*(?:per year|/(?:year|yr|annum|hr|month)))?',
    # "$176,000 CAD - $200,000 CAD" (CAD after each amount)
    r'\$[\d,.]+[kK]?\s*CAD\s*[-–—]\s*\$[\d,.]+[kK]?\s*CAD',
    # "$120,000 - $150,000 CAD" or "$252,000- $308,000" or "$120,000 to $150,000"
    r'\$[\d,.]+[kK]?\s*(?:[-–—]|\bto\b)\s*\$[\d,.]+[kK]?(?:\s*(?:CAD|USD|per year|per month|/(?:year|yr|annum|hr|month)))?',
    # "$190K-220K" (second value may omit $, K required on both)
    r'\$[\d,.]+[kK]\s*[-–—]\s*\$?[\d,.]+[kK]',
    # "$75-85/hr" or "$90-95 per hour"
    r'\$\d+\s*[-–—]\s*\$?\d+\s*(?:/hr|per hour)',
    # "125,000-165,000 CAD" (no $ prefix, CAD/USD suffix required)
    r'[\d,.]+[kK]?\s*[-–—]\s*[\d,.]+[kK]?\s*(?:CAD|USD)(?:\s*/\s*(?:Year|year|yr))?',
]

MIN_ANNUAL_SALARY = 40000
MIN_HOURLY_RATE = 30
MIN_MONTHLY_SALARY = 5000
FETCH_MAX_WORKERS = 10

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def extract_numbers(text):
    """Extract numeric values from salary text, handling k/K suffix."""
    nums = []
    for m in re.finditer(r'([\d,.]+)\s*([kK])?', text):
        raw = m.group(1).replace(',', '')
        try:
            val = float(raw)
            if m.group(2):
                val *= 1000
            nums.append(val)
        except ValueError:
            continue
    return nums


def is_plausible_salary(text, nums):
    """Return True if the numbers look like a real salary, not noise."""
    if not nums:
        return False
    is_hourly = bool(re.search(r'/hr|per hour', text, re.IGNORECASE))
    is_monthly = bool(re.search(r'per month|/month', text, re.IGNORECASE))
    max_val = max(nums)
    if is_hourly:
        return max_val >= MIN_HOURLY_RATE
    if is_monthly:
        return max_val >= MIN_MONTHLY_SALARY
    return max_val >= MIN_ANNUAL_SALARY


def extract_salary(text):
    """Extract salary range from description text. Returns raw matched string or None."""
    clean = text.replace('\\-', '-').replace('\\$', '$').replace('\\.', '.')
    clean = re.sub(r'<[^>]+>', ' ', clean)
    clean = re.sub(r'\*+', '', clean)
    clean = re.sub(r'\s+', ' ', clean)

    for pattern in SALARY_PATTERNS:
        for match in re.finditer(pattern, clean, re.IGNORECASE):
            matched = match.group(0)
            nums = extract_numbers(matched)
            if is_plausible_salary(matched, nums):
                return matched.strip()
    return None


def normalize_salary(raw):
    """Clean extracted salary for table display."""
    if not raw:
        return None
    s = re.sub(r'\s+', ' ', raw).strip()
    s = re.sub(r'^(?:salary|compensation|pay|range|base)[:\s]*',
               '', s, flags=re.IGNORECASE)
    if len(s) > 60:
        s = s[:57] + "..."
    return s


def _extract_linkedin_description(html):
    """Extract job description from LinkedIn guest page, ignoring salary estimate widget."""
    m = re.search(
        r'class="show-more-less-html__markup[^"]*"[^>]*>(.*?)</div>',
        html, re.DOTALL,
    )
    return m.group(1) if m else ""


def _fetch_salary_from_url(url):
    """Fetch a job URL and extract salary from the HTML. Returns normalized salary or None."""
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=15, allow_redirects=True)
        resp.raise_for_status()

        if "linkedin.com/jobs/view" in url:
            text = _extract_linkedin_description(resp.text)
        else:
            text = resp.text

        raw = extract_salary(text)
        return normalize_salary(raw) if raw else None
    except Exception as e:
        log.error("Failed to fetch salary from %s: %s", url, e)
        return None


def enrich_salaries(jobs):
    """Add salary to jobs from descriptions, with URL fetch fallback.

    Pass 1: Extract salary from description text (fast, no network).
    Pass 2: For jobs still missing salary with no description, fetch the URL directly.

    Mutates and returns the input list.
    """
    needs_fetch = []
    for job in jobs:
        if job.get("salary") is not None:
            continue
        desc = job.get("description", "")
        if desc:
            raw = extract_salary(desc)
            if raw:
                job["salary"] = normalize_salary(raw)
        if job.get("salary") is None and not desc and job.get("url"):
            needs_fetch.append(job)

    if needs_fetch:
        log.info("Fetching %d URLs for salary data...", len(needs_fetch))
        with ThreadPoolExecutor(max_workers=FETCH_MAX_WORKERS) as pool:
            futures = {pool.submit(_fetch_salary_from_url, j["url"]): j for j in needs_fetch}
            for future in as_completed(futures):
                job = futures[future]
                try:
                    salary = future.result()
                except Exception as e:
                    log.error("Unexpected error fetching %s: %s", job.get("url"), e)
                    continue
                if salary:
                    job["salary"] = salary

    return jobs
