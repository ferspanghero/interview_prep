# Design: Company Research Command

## Context

When reviewing `pending_review.md`, Glassdoor and Blind ratings help quickly filter out red-flag employers. Currently this is done manually by launching parallel agents. This command automates that into a repeatable `/research-companies` skill that outputs structured data to `companies.json` and displays a sorted summary table.

## Folder Structure (additions only)

```
interview_prep/
  jobs_scraping/
    listings/
      companies.json            # Company ratings cache (created/updated by command)
    plan_v2.md                  # This design doc
  .claude/commands/
    research-companies.md       # Slash command: research company ratings
```

## Data Format: companies.json

```json
[
  {
    "company": "Asana",
    "glassdoor": 4.1,
    "blind": 4.0,
    "notes": ""
  }
]
```

- Scores are floats (e.g., 4.1) or `null` if not found
- Notes capture red flags: few reviews, low sub-scores, big platform divergence

## Slash Command: /research-companies

### Modes

| Invocation | Behavior |
|------------|----------|
| `/research-companies` | Research new companies in `pending_review.md` not already in `companies.json` |
| `/research-companies refresh` | Re-research ALL companies (ignore cache) |
| `/research-companies Asana` | Research only that company |

### Steps

1. Read `jobs_scraping/listings/pending_review.md`, extract unique company names
2. Read `jobs_scraping/listings/companies.json` if it exists — skip companies already researched (unless `refresh`)
3. Normalize company names for matching (e.g., "JOBBER" = "Jobber", "Microsoft AI" = "Microsoft")
4. For each batch of ~5 new companies, launch parallel agents that:
   - WebSearch `"[company] glassdoor rating"` → extract overall score (X.X / 5)
   - WebSearch `"[company] teamblind rating"` → extract overall score (X.X / 5)
   - Note review count and red flags (very few reviews, low management/career-growth sub-scores, big platform divergence)
   - Return results as: `Company | Glassdoor | Blind | Notes`
   - Use `null` for scores that can't be found
5. Merge new results into `companies.json`
6. Display full table sorted by median score (desc):

```
| Company | Glassdoor | Blind | Median | Notes |
|---------|-----------|-------|--------|-------|
```

Median = average of both scores if both exist, or the single available score. Companies with no scores at the bottom.

### Sources

Glassdoor + Blind only. Most relevant for SWE roles.

## Implementation

No Python script needed. The skill is a Claude command definition (`.claude/commands/research-companies.md`) that uses WebSearch + agent parallelization — same pattern as the manual research, codified into a repeatable instruction set.

## Job Lifecycle (updated from v1)

```
/search-jobs → scrape → enrich salaries → filter → dedup → append to pending_review.md
                                                                  ↓
                                                        /research-companies
                                                        → fetch Glassdoor/Blind ratings
                                                        → write companies.json
                                                        → display sorted table
                                                                  ↓
                                                        User reviews pending_review.md + ratings
                                                          ↓                    ↓
                                            /ignore-jobs               /apply-to-job
```

## Verification

1. Run `/research-companies` — should produce `companies.json` and display a sorted table
2. Run `/research-companies` again — should skip already-researched companies
3. Run `/research-companies refresh` — should re-research all
4. Run `/research-companies Asana` — should research only Asana
