Ignore jobs from the pending review list.

The user will describe jobs to ignore in plain English (e.g., "ignore the Stripe backend role and the Notion one").

1. Read `jobs_scraping/listings/pending_review.md` to find the matching jobs
2. Extract their URLs exactly as they appear in the table (do not modify or truncate them)
3. If ambiguous (e.g., multiple Stripe roles), ask the user which one
4. Run: `python3 jobs_scraping/scripts/orchestrator.py --ignore <url1> <url2> ...`
5. If the user says "block", "block_company", or similar, also run: `python3 jobs_scraping/scripts/orchestrator.py --block_company <company1> <company2> ...` using the unique company names from the ignored jobs. This prevents future jobs from these companies from appearing in searches. Do NOT block by default — only when explicitly requested.
6. Confirm what was removed (and which companies were blocked, if any)
