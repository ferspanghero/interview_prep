Enrich missing salary data in the pending review list using LLM-powered web fetching.

1. Read `jobs_scraping/listings/pending_review.md`
2. Find all jobs with "—" in the Salary column
3. For each, use WebFetch to visit the job URL. Use the prompt: "Extract any salary, compensation, or pay range mentioned on this page. Return the exact text if found, or NO_SALARY."
4. If WebFetch returns a redirect, follow it with another WebFetch call
5. For jobs where salary is found, update the Salary column in pending_review.md directly
6. Report a summary: how many checked, how many enriched, which ones

Use maximum parallelism with WebFetch calls. Skip jobs where the URL is likely to block (Indeed direct links typically return 403).
