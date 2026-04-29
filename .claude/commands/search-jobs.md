Run the job search aggregator to find new Senior/Staff SWE roles, then auto-enrich the new jobs with company ratings.

1. Run: `python3 jobs_scraping/scripts/orchestrator.py`
2. Show the summary from the orchestrator output (scraped, excluded, filtered, new jobs, salary coverage, AI roles)
3. From `jobs_scraping/listings/pending_review.md`, identify the jobs the orchestrator added in this run (match by the "New jobs" count and the rows appended to the file)
4. **Auto-research new companies**: extract unique company names from the new jobs, then invoke `/research-companies` logic for any company not already in `jobs_scraping/listings/companies.json`. Skip entirely if zero new jobs were added.
5. Display the new jobs as a single merged table, sorted by median rating descending (no-rating companies last):

    | Company | Role | Salary | Location | AI | Glassdoor | Blind | Median | Public | Notes |
    |---------|------|--------|----------|----|-----------|-------|--------|--------|-------|

    Pull rating columns from `companies.json` after step 4. Use `—` for missing values. Notes capture red flags only.

If the user wants to filter by source, run with `--source jobspy|remotive|wwr`.
If the user wants to limit results, run with `--limit N`.
If the user wants to control freshness, run with `--hours_old N` (default: 168 = 7 days).
