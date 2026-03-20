import logging
import logging_config
import math
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from jobspy import scrape_jobs
from salary_enricher import enrich_salaries

log = logging.getLogger(__name__)

SEARCH_TERMS = [
    '"senior software engineer"',
    '"staff software engineer"',
    '"senior backend engineer"',
    '"staff backend engineer"',
]

LOCATIONS = [
    "Vancouver, BC",
    "Canada",
]

SITES = [
    {"site_name": ["indeed"], "extra_kwargs": {"country_indeed": "Canada"}},
    {"site_name": ["linkedin"], "extra_kwargs": {"linkedin_fetch_description": True}},
]

SOURCE_LABELS = {
    "indeed": "Indeed",
    "linkedin": "LinkedIn",
}


def _clean_title(title):
    return re.split(r"\s*\|", title)[0].strip()


def _scrape_one(term, location, site_config, limit):
    site = site_config["site_name"][0]
    results = scrape_jobs(
        site_name=site_config["site_name"],
        search_term=term,
        location=location,
        results_wanted=limit,
        **site_config["extra_kwargs"],
    )
    return results, site


def _process_results(results, site_fallback):
    jobs = []
    for _, row in results.iterrows():
        url = row.get("job_url", "")
        company = row.get("company", "")
        if not url:
            continue
        if not company or (isinstance(company, float) and math.isnan(company)):
            company = "Unknown"

        posted = row.get("date_posted")
        if posted is not None:
            posted = str(posted)[:10]

        direct_url = row.get("job_url_direct", "")
        if not direct_url or str(direct_url) == "nan":
            direct_url = url

        site = str(row.get("site", site_fallback))
        source = SOURCE_LABELS.get(site, site.title())

        jobs.append({
            "title": _clean_title(row.get("title", "")),
            "company": company,
            "location": row.get("location", ""),
            "salary": None,
            "url": direct_url,
            "source": source,
            "posted": posted,
            "description": str(row.get("description", "") or ""),
        })
    return jobs


def fetch(limit=50):
    all_jobs = {}
    searches = [(t, l, s) for t in SEARCH_TERMS for l in LOCATIONS for s in SITES]
    log.info("Running %d searches across Indeed + LinkedIn", len(searches))

    with ThreadPoolExecutor() as pool:
        futures = {}
        for term, location, site_config in searches:
            f = pool.submit(_scrape_one, term, location, site_config, limit)
            futures[f] = site_config["site_name"][0]

        for future in as_completed(futures):
            site_label = futures[future]
            try:
                results, site_fallback = future.result()
                for job in _process_results(results, site_fallback):
                    if job["url"] not in all_jobs:
                        all_jobs[job["url"]] = job
            except Exception as e:
                log.error("%s search failed: %s", site_label, e)

    log.info("Jobspy: %d unique jobs, enriching salaries...", len(all_jobs))
    enriched = enrich_salaries(list(all_jobs.values()))
    with_salary = sum(1 for j in enriched if j.get("salary"))
    log.info("Jobspy: %d/%d jobs have salary data", with_salary, len(enriched))
    return enriched


if __name__ == "__main__":
    logging_config.setup()
    results = fetch(limit=5)
    print(f"Found {len(results)} jobs")
    for job in results[:10]:
        print(f"  [{job['source']}] {job['title']} | {job['company']} | {job['location']} | {job['salary']}")
