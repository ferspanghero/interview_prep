Ignore jobs from the pending review list.

The user will describe jobs to ignore in plain English (e.g., "ignore the Stripe backend role and the Notion one").

1. Read `jobs_scraping/listings/pending_review.md` to find the matching jobs
2. Extract their URLs from the table
3. If ambiguous (e.g., multiple Stripe roles), ask the user which one
4. Run: `python3 jobs_scraping/scripts/orchestrator.py --ignore <url1> <url2> ...`
5. Confirm what was removed
