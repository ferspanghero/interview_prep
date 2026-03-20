import json
import logging
import logging_config
import urllib.request

log = logging.getLogger(__name__)

API_URL = "https://remotive.com/api/remote-jobs?category=software-dev&limit={limit}"
HTTP_TIMEOUT = 30


def fetch(limit=100):
    url = API_URL.format(limit=limit)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    resp = urllib.request.urlopen(req, timeout=HTTP_TIMEOUT)
    data = json.loads(resp.read())

    jobs = []
    for item in data.get("jobs", []):
        jobs.append({
            "title": item.get("title", ""),
            "company": item.get("company_name", ""),
            "location": item.get("candidate_required_location", ""),
            "salary": item.get("salary") or None,
            "url": item.get("url", ""),
            "source": "Remotive",
            "posted": item.get("publication_date", ""),
            "description": item.get("description", ""),
        })

    log.info("Remotive: %d jobs fetched", len(jobs))
    return jobs


if __name__ == "__main__":
    logging_config.setup()
    results = fetch(limit=10)
    print(f"Found {len(results)} jobs")
    for job in results[:5]:
        print(f"  {job['title']} | {job['company']} | {job['location']} | {job['salary']}")
