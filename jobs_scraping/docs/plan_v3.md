# V3: Company Blocklist

Adds a company-level blocklist to automatically filter out jobs from unwanted companies during scraping.

## Schema

`companies.json` gains a `blocked` boolean field (default `false`). Blocked companies are filtered out during `search()` before any other filters run.

## Filter Behavior

- Case-insensitive **exact match** on company name (blocking "Microsoft" does NOT block "Microsoft AI")
- Blocked jobs are logged and counted in the summary output
- Missing `companies.json` gracefully skips the filter

## Blocking Companies

`orchestrator.py --block_company <name1> <name2> ...`

- If the company exists in `companies.json`: sets `blocked: true`
- If the company doesn't exist: creates a minimal entry with `blocked: true` and null ratings
- Case-insensitive lookup against existing entries

## Slash Commands

- **`/block-companies`** — block companies directly (e.g., `/block-companies giga, omnissa`)
- **`/ignore-jobs`** — accepts an optional "block_company" instruction. When specified, after ignoring the job URLs, it also runs `--block_company` with the unique company names from the ignored jobs. Default behavior (no blocking) is unchanged.

## companies.json Entry Format

```json
{
  "company": "Giga",
  "glassdoor": 4.3,
  "blind": null,
  "public": false,
  "blocked": true,
  "notes": "Only 7 reviews"
}
```
