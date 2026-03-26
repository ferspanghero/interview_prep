Run the job search aggregator to find new Senior/Staff SWE roles.

1. Run: `python3 jobs_scraping/scripts/orchestrator.py`
2. Show the summary from the orchestrator output (scraped, excluded, filtered, new jobs, salary coverage, AI roles)
3. From `jobs_scraping/listings/pending_review.md`, display only the jobs that the orchestrator added in this run (match by the "New jobs" count and the last N rows appended to the file)

If the user wants to filter by source, run with `--source jobspy|remotive|wwr`.
If the user wants to limit results, run with `--limit N`.
If the user wants to control freshness, run with `--hours_old N` (default: 168 = 7 days).
