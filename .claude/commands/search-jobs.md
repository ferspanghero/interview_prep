Run the job search aggregator to find new Senior/Staff SWE roles.

1. Run: `python3 jobs_scraping/scripts/orchestrator.py`
2. Read `jobs_scraping/listings/pending_review.md` and display the full table to the user
3. Show the summary from the orchestrator output (scraped, excluded, filtered, new jobs, salary coverage, AI roles)

If the user wants to filter by source, run with `--source jobspy|remotive|wwr`.
If the user wants to limit results, run with `--limit N`.
