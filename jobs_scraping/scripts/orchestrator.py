import json
import logging
import os
import sys

import logging_config
from scrapers import jobspy_scraper, remotive, wwr
import filters
from exporter import append_jobs, remove_jobs
from utils import normalize_url

log = logging.getLogger(__name__)

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
LISTINGS_DIR = os.path.join(BASE_DIR, "listings")
PENDING_PATH = os.path.join(LISTINGS_DIR, "pending_review.md")
SCRAPED_PATH = os.path.join(LISTINGS_DIR, "already_scraped.json")
IGNORE_PATH = os.path.join(LISTINGS_DIR, "ignored.json")
APPLIED_PATH = os.path.join(LISTINGS_DIR, "applied.json")
COMPANIES_PATH = os.path.join(LISTINGS_DIR, "companies.json")


def _load_json_list(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)


def _save_json_list(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _load_blocked_companies(companies_path):
    if not os.path.exists(companies_path):
        return set()
    with open(companies_path) as f:
        companies = json.load(f)
    return {c["company"].strip().lower() for c in companies if c.get("blocked")}


def _load_excluded_urls(scraped_path, ignore_path, applied_path):
    urls = set(_load_json_list(scraped_path))
    urls.update(_load_json_list(ignore_path))
    urls.update(_load_json_list(applied_path))
    return urls


def search(
    sources=None,
    limit=50,
    hours_old=168,
    pending_path=PENDING_PATH,
    scraped_path=SCRAPED_PATH,
    ignore_path=IGNORE_PATH,
    applied_path=APPLIED_PATH,
    companies_path=COMPANIES_PATH,
):
    if sources is None:
        sources = ["jobspy", "remotive", "wwr"]

    excluded_urls = _load_excluded_urls(scraped_path, ignore_path, applied_path)
    blocked_companies = _load_blocked_companies(companies_path)
    log.info("Excluded URLs: %d (scraped/ignored/applied)", len(excluded_urls))
    if blocked_companies:
        log.info("Blocked companies: %d", len(blocked_companies))

    all_jobs = []
    scrapers = {
        "jobspy": jobspy_scraper.fetch,
        "remotive": remotive.fetch,
        "wwr": wwr.fetch,
    }

    for source in sources:
        fetcher = scrapers.get(source)
        if not fetcher:
            continue
        try:
            log.info("Scraping %s...", source)
            kwargs = {"limit": limit}
            if source == "jobspy":
                kwargs["hours_old"] = hours_old
            jobs = fetcher(**kwargs)
            log.info("  %s returned %d jobs", source, len(jobs))
            all_jobs.extend(jobs)
        except Exception as e:
            log.error("  %s scraper failed: %s", source, e)

    log.info("Total scraped: %d", len(all_jobs))

    new_jobs = []
    seen_urls = set()
    filtered = {"blocked": 0, "title": 0, "excluded": 0, "location": 0, "salary": 0}
    for job in all_jobs:
        url = normalize_url(job.get("url", ""))
        job["url"] = url
        if not url or url in excluded_urls or url in seen_urls:
            continue
        seen_urls.add(url)

        title = job.get("title", "")
        company = job.get("company", "")
        location = job.get("location", "")

        if company.strip().lower() in blocked_companies:
            filtered["blocked"] += 1
            log.info("  Blocked: %s - %s", company, title)
            continue

        if not filters.matches_title(title):
            filtered["title"] += 1
            continue
        if filters.is_excluded(title):
            filtered["excluded"] += 1
            continue
        if not filters.matches_location(location):
            filtered["location"] += 1
            continue

        job["is_ai"] = filters.is_ai_role(title, job.get("description", ""))
        if not filters.matches_salary(job.get("salary")):
            filtered["salary"] += 1
            log.info("  Salary filtered: %s - %s (%s)", company, title, job.get("salary"))
            continue
        new_jobs.append(job)

    if new_jobs:
        append_jobs(new_jobs, pending_path)
        scraped = set(_load_json_list(scraped_path))
        scraped.update(job["url"] for job in new_jobs)
        _save_json_list(scraped_path, sorted(scraped))

    with_salary = sum(1 for j in new_jobs if j.get("salary"))
    ai_count = sum(1 for j in new_jobs if j.get("is_ai"))

    log.info("--- Summary ---")
    log.info("  Scraped:    %d total", len(all_jobs))
    log.info("  Excluded:   %d (already scraped/ignored/applied)", len(excluded_urls))
    log.info("  Filtered:   %d blocked, %d title, %d excluded role, %d location, %d salary",
             filtered["blocked"], filtered["title"], filtered["excluded"],
             filtered["location"], filtered["salary"])
    log.info("  New jobs:   %d", len(new_jobs))
    log.info("  With salary: %d/%d", with_salary, len(new_jobs))
    log.info("  AI roles:   %d/%d", ai_count, len(new_jobs))

    return new_jobs


def ignore(
    urls,
    pending_path=PENDING_PATH,
    ignore_path=IGNORE_PATH,
    scraped_path=SCRAPED_PATH,
):
    urls = [normalize_url(u) for u in urls]
    ignored = set(_load_json_list(ignore_path))
    ignored.update(urls)
    _save_json_list(ignore_path, sorted(ignored))

    remove_jobs(urls, pending_path)

    scraped = _load_json_list(scraped_path)
    scraped = [u for u in scraped if u not in set(urls)]
    _save_json_list(scraped_path, scraped)

    log.info("Ignored %d jobs", len(urls))


def apply(
    url,
    pending_path=PENDING_PATH,
    applied_path=APPLIED_PATH,
):
    url = normalize_url(url)
    applied = set(_load_json_list(applied_path))
    applied.add(url)
    _save_json_list(applied_path, sorted(applied))

    remove_jobs([url], pending_path)

    log.info("Applied: %s", url)


def block_company(
    company_names,
    companies_path=COMPANIES_PATH,
):
    if os.path.exists(companies_path):
        with open(companies_path) as f:
            companies = json.load(f)
    else:
        companies = []

    existing = {c["company"].strip().lower(): c for c in companies}

    for name in company_names:
        key = name.strip().lower()
        if key in existing:
            existing[key]["blocked"] = True
        else:
            companies.append({
                "company": name,
                "glassdoor": None,
                "blind": None,
                "public": False,
                "blocked": True,
                "notes": "",
            })

    os.makedirs(os.path.dirname(companies_path), exist_ok=True)
    with open(companies_path, "w") as f:
        json.dump(companies, f, indent=2)

    log.info("Blocked %d companies", len(company_names))


if __name__ == "__main__":
    import argparse

    logging_config.setup()

    parser = argparse.ArgumentParser(description="Job search orchestrator")
    parser.add_argument("--source", choices=["jobspy", "remotive", "wwr", "all"], default="all")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--hours_old", type=int, help="Only fetch jobs posted within N hours (default: 168)")
    parser.add_argument("--ignore", nargs="+", help="URLs to ignore")
    parser.add_argument("--apply", dest="apply_url", help="URL to mark as applied")
    parser.add_argument("--block_company", nargs="+", help="Company names to block")

    args = parser.parse_args()

    if args.block_company:
        block_company(args.block_company)
    elif args.ignore:
        ignore(args.ignore)
    elif args.apply_url:
        apply(args.apply_url)
    else:
        sources = None if args.source == "all" else [args.source]
        search(sources=sources, limit=args.limit, hours_old=args.hours_old)
