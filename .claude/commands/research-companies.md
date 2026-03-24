Research Glassdoor and Blind ratings for companies in the pending review list: $ARGUMENTS

## Steps

1. Read `jobs_scraping/listings/pending_review.md` and extract unique company names
2. Read `jobs_scraping/listings/companies.json` if it exists — these companies are already researched
3. Determine which companies to research based on $ARGUMENTS:
   - **No arguments**: research only companies NOT already in `companies.json`
   - **"refresh"**: re-research ALL companies in `pending_review.md` (ignore cache)
   - **A company name**: research only that specific company
4. Normalize company names for matching (e.g., "JOBBER" = "Jobber", "Microsoft AI" = "Microsoft")
5. For each batch of ~5 new companies, launch parallel agents. Each agent should:
   - WebSearch `"[company] glassdoor rating"` → extract overall score (X.X out of 5)
   - WebSearch `"[company] teamblind rating"` → extract overall score (X.X out of 5)
   - Note review count and any red flags (very few reviews, low management/career-growth sub-scores, big divergence between platforms)
   - Determine if the company is publicly traded (true/false)
   - Return results as: `Company | Glassdoor | Blind | Public | Notes`
   - Use `null` for scores that can't be found (company too small, no profile on that platform)
6. Merge new results into `jobs_scraping/listings/companies.json`. Existing entries are preserved unless refreshing.
7. Display the full table sorted by median score descending:

```
| Company | Glassdoor | Blind | Median | Public | Notes |
|---------|-----------|-------|--------|--------|-------|
```

Median = average of both scores if both exist, or the single available score if only one exists. Companies with no scores go at the bottom.

## companies.json format

```json
[
  {
    "company": "Asana",
    "glassdoor": 4.1,
    "blind": 4.0,
    "public": true,
    "blocked": false,
    "notes": ""
  }
]
```

Scores are floats or null. Notes capture red flags only — keep them short.
