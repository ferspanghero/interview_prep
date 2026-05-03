Block companies from appearing in future job searches: $ARGUMENTS

The user will list company names in plain English (e.g., "giga, omnissa").

1. Read `jobs_scraping/listings/pending_review.md` and find URLs of any rows whose company matches one of the names being blocked (case-insensitive)
2. Extract those URLs exactly as they appear in the table (do not modify or truncate)
3. If matching URLs exist, run: `python3 jobs_scraping/scripts/orchestrator.py --ignore <url1> <url2> ...`
4. Run: `python3 jobs_scraping/scripts/orchestrator.py --block_company <company1> <company2> ...`
5. Confirm which companies were blocked and how many pending jobs were removed
