# Design: Job Search Aggregator

## Context

Job search tool for Senior/Staff SWE roles. Systematically discovers opportunities across multiple job boards, filters by criteria, and manages a pipeline from discovery → review → apply or ignore. Location filters are configurable (defaults to remote Canada / hybrid Vancouver as an example).

## Folder Structure

```
interview_prep/
  jobs_scraping/
    scripts/
      scrapers/
        jobspy_scraper.py   # Indeed + LinkedIn via JobSpy (with salary enrichment)
        remotive.py         # Remotive JSON API
        wwr.py              # We Work Remotely RSS
      filters.py            # Shared filtering (title, location, salary, AI flag, exclusions)
      salary_enricher.py    # Scraper-agnostic salary extraction from descriptions
      orchestrator.py       # Runs scrapers, dedupes, filters, appends to pending_review.md
      exporter.py           # Formats markdown table, handles ignore/apply operations
      logging_config.py     # Shared logging configuration
    listings/
      already_scraped.json  # URLs already in pending_review.md (dedup)
      ignored.json          # Job URLs manually dismissed
      applied.json          # Job URLs applied to (URL list)
      pending_review.md     # Living list of jobs not yet acted on
      applications.md       # Detailed application tracking (comp, status, notes)
    plan_v1.md              # This design doc
  .claude/commands/
    search-jobs.md          # Slash command: scrape and show results
    ignore-jobs.md          # Slash command: dismiss jobs
    apply-to-job.md         # Slash command: apply to a job and track it
```

## Sources

| Source | Method | Salary Data | Quality | Notes |
|--------|--------|-------------|---------|-------|
| Indeed + LinkedIn | JobSpy library | Extracted from descriptions via regex | High volume | LinkedIn descriptions fetched via `linkedin_fetch_description=True` |
| Remotive | JSON API | Yes (from API) | Good, remote-only | Best structured salary data |
| We Work Remotely | RSS feed | No | Good, low volume | Filter stale listings (>30 days) |

## Salary Enrichment

`salary_enricher.py` is a scraper-agnostic module that enriches jobs with salary data extracted from descriptions. It:
- Receives a list of job dicts with `salary` and `description` keys
- For jobs where `salary` is None, extracts salary from `description` via 8 regex patterns
- Covers formats: CA$, C$, CAD, $range, $Xk, hourly, monthly
- Validates plausibility (rejects fundraising amounts, stipends, etc.)
- Called by `jobspy_scraper.fetch()` after scraping

## Filters

- **Title match**: `(senior|staff|lead|principal).*(software|backend|platform|swe|fullstack|full.stack)`
- **Location match**: `vancouver|british columbia|\bbc\b|worldwide|anywhere` + `\bremote\b` (case-insensitive). Rejects bare "Canada", rejects "Remote (US)".
- **Salary floor**: $200K+ CAD where salary data available. Jobs without salary pass through. Hourly/monthly rates pass through (need conversion context).
- **AI flag**: Mark `[AI]` if title or description matches `\b(ai|ml|llm|agent|rag|nlp|machine.learning|artificial.intelligence)\b`. Flag only, don't filter.
- **Exclude**: `\b(junior|intern|manager|director|contractor|contract)\b` in title

## Export: pending_review.md

Single file, seamless append. New jobs sorted by company name. No row numbers — the LLM matches jobs by natural language description.

```markdown
# Active Jobs

| Company | Role | Salary | Location | AI | Source | Posted | Scraped | URL |
|---------|------|--------|----------|----|--------|--------|---------|-----|
| Stripe | Sr. Backend Eng | $200K-$280K | Remote-CA | | Indeed | 2026-03-18 | 2026-03-19 | [link](url) |
| Anthropic | Staff SWE, AI Infra | $250K-$350K | Remote | [AI] | Remotive | 2026-03-17 | 2026-03-19 | [link](url) |
```

## Job Lifecycle

```
/search-jobs → scrape → enrich salaries → filter → dedup → append to pending_review.md
                                                                  ↓
                                                        User reviews pending_review.md
                                                          ↓                    ↓
                                            "ignore the Stripe one"    "apply to the Anthropic role"
                                                          ↓                    ↓
                                            LLM reads pending_review   LLM reads pending_review
                                            finds URL, runs:           finds URL, runs:
                                            orchestrator --ignore URL  /apply-to-job
                                                          ↓                    ↓
                                                  ignored.json           applied.json (URL)
                                                  row removed            applications.md (details)
                                                  from pending           row removed from pending
```

## Script Design

### Each scraper (jobspy_scraper.py, remotive.py, wwr.py)

- Exports a `fetch(limit=50) -> list[dict]` function
- Returns normalized dicts:
  ```python
  {
      "title": str,
      "company": str,
      "location": str,
      "salary": str | None,      # Enriched from description by salary_enricher
      "url": str,
      "source": str,             # "Indeed" | "LinkedIn" | "Remotive" | "WWR"
      "posted": str | None,      # ISO date or None
      "description": str,        # Full job description text
  }
  ```
- Can be run standalone for testing: `python3 jobspy_scraper.py`
- jobspy_scraper calls `enrich_salaries()` before returning

### salary_enricher.py

- `extract_salary(text) -> str | None` — regex salary extraction from description text
- `normalize_salary(raw) -> str | None` — cleanup for table display
- `enrich_salaries(jobs) -> list[dict]` — public API: enriches jobs in-place, returns same list

### filters.py

- `matches_title(title) -> bool`
- `matches_location(location) -> bool`
- `is_excluded(title) -> bool`
- `is_ai_role(title, description="") -> bool`
- `matches_salary(salary, min_annual=200000) -> bool`

### orchestrator.py

Main entry point. Three modes:

**Search mode** (default):
```
python3 orchestrator.py [--source jobspy|remotive|wwr|all] [--limit N]
```
- Imports each scraper's `fetch()`
- Applies filters from `filters.py`
- Deduplicates against already_scraped.json + ignored.json + applied.json
- Calls exporter to append new jobs to pending_review.md
- Updates already_scraped.json with new URLs
- Prints summary (scraped, excluded, filtered, new jobs, salary coverage, AI roles)

**Ignore mode**:
```
python3 orchestrator.py --ignore url1 url2 ...
```
- Adds URLs to ignored.json
- Removes matching rows from pending_review.md
- Removes URLs from already_scraped.json

**Apply mode**:
```
python3 orchestrator.py --apply url
```
- Adds URL to applied.json (URL list, no metadata)
- Removes matching row from pending_review.md

### exporter.py

- `append_jobs(jobs, path)` — appends new rows, sorted by company
- `remove_jobs(urls, path)` — removes rows matching URLs

## Slash Commands

### /search-jobs

Runs the scraper script, reads and displays pending_review.md, shows summary counts.

### /ignore-jobs

Takes natural language. The LLM reads pending_review.md, matches the user's description to specific jobs, extracts URLs, and runs `orchestrator.py --ignore`.

### /apply-to-job

Takes a URL or natural language description. Reads the job posting, extracts details, asks user to confirm, then:
1. Appends detailed entry to `listings/applications.md`
2. Runs `orchestrator.py --apply <url>` to mark as applied

## JobSpy Search Strategy

Run 4 separate searches per site (Indeed + LinkedIn) × 2 locations, parallelized via ThreadPoolExecutor. LinkedIn descriptions fetched via `linkedin_fetch_description=True` for salary enrichment.

Search terms:
1. `"senior software engineer"`
2. `"staff software engineer"`
3. `"senior backend engineer"`
4. `"staff backend engineer"`

Locations: `"Vancouver, BC"`, `"Canada"`

## Dependencies

- `python-jobspy` — Indeed + LinkedIn scraping
- Python 3 standard library only for everything else

## Verification

1. Run each scraper standalone — confirm it returns relevant jobs
2. Run orchestrator — confirm filtering works (senior/staff only, no junior, AI flagged, salary >= $200K)
3. Run twice — second run should append only new jobs
4. Test ignore: describe a job, confirm it's removed from pending_review.md and added to ignored.json
5. Test apply: describe a job, confirm it's removed from pending_review.md and added to applied.json
