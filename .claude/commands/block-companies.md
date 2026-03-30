Block companies from appearing in future job searches: $ARGUMENTS

The user will list company names in plain English (e.g., "giga, omnissa").

1. Read `jobs_scraping/listings/pending_review.md` and find any jobs from the companies being blocked
2. If matching jobs exist, run `/ignore-jobs` to remove them from pending review first
3. Run: `python3 jobs_scraping/scripts/orchestrator.py --block_company <company1> <company2> ...`
4. Confirm which companies were blocked and how many pending jobs were removed
