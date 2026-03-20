import logging
import logging_config
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

log = logging.getLogger(__name__)

RSS_URL = "https://weworkremotely.com/categories/remote-programming-jobs.rss"
STALE_DAYS = 30
HTTP_TIMEOUT = 30


def _parse_date(date_str):
    try:
        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def _parse_company_and_title(raw_title):
    if ": " in raw_title:
        parts = raw_title.split(": ", 1)
        return parts[0].strip(), parts[1].strip()
    return "", raw_title


def fetch(limit=50):
    req = urllib.request.Request(RSS_URL, headers={"User-Agent": "Mozilla/5.0"})
    resp = urllib.request.urlopen(req, timeout=HTTP_TIMEOUT)
    rss = resp.read().decode("utf-8")
    root = ET.fromstring(rss)

    cutoff = datetime.now(timezone.utc) - timedelta(days=STALE_DAYS)
    jobs = []

    for item in root.findall(".//item"):
        raw_title = item.find("title").text if item.find("title") is not None else ""
        link = item.find("link").text if item.find("link") is not None else ""
        pub_date_str = item.find("pubDate").text if item.find("pubDate") is not None else ""

        pub_dt = None
        try:
            pub_dt = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %z")
            if pub_dt < cutoff:
                continue
        except (ValueError, TypeError):
            pass

        company, title = _parse_company_and_title(raw_title)

        jobs.append({
            "title": title,
            "company": company,
            "location": "Remote",
            "salary": None,
            "url": link,
            "source": "WWR",
            "posted": pub_dt.strftime("%Y-%m-%d") if pub_dt else None,
        })

        if len(jobs) >= limit:
            break

    log.info("WWR: %d jobs fetched", len(jobs))
    return jobs


if __name__ == "__main__":
    logging_config.setup()
    results = fetch(limit=10)
    print(f"Found {len(results)} jobs")
    for job in results[:5]:
        print(f"  {job['company']}: {job['title']} | {job['posted']}")
