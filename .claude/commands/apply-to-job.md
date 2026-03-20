Apply to a job. The user provides a URL or describes a job from `jobs_scraping/listings/pending_review.md` in plain English (e.g., "apply to the Databricks backend one"): $ARGUMENTS

If the user references a job by description, read `jobs_scraping/listings/pending_review.md` to find the matching URL. If ambiguous, ask which one.

If the user provides a URL directly, use that — the job may or may not be in pending_review.md.

## Step 1: Read the job posting

Read the ENTIRE job posting thoroughly — do not skim. Pay close attention to compensation sections, pay bands, salary ranges, and level information which are often at the bottom of the page or in fine print.

Extract what you can (company, role title, location, comp range if listed), then ask the user to confirm or fill in anything missing:
- Status (default: Applied)
- Date applied (default: today)
- Comp range (if not in the posting)
- Next action and date (e.g., "follow up if no response by April 1")
- Public (Yes/No — whether the company is publicly traded. If you don't know, research it. If the company is private, also research and note: latest valuation, any known equity liquidity options like buyback programs or secondary sale opportunities)
- Any notes

## Compensation format

All comp should be shown as a total in CAD. Use 1.35 USD to CAD conversion rate for any USD components. Format the Comp Range column as:

**Total CAD value** — breakdown of each component in CAD, with original currency in parentheses if converted.

Example: `$527K CAD — $217K base (CAD) + $33K bonus (15%, CAD) + $278K equity ($206K USD × 1.35)`

Components may be in CAD or USD depending on the company — ask the user to clarify the currency for each component. Always convert to CAD for the total and show the original value when converted.

## Step 2: Track the application

Once confirmed:
1. Append a new row to `jobs_scraping/listings/applications.md` with the details
2. Run: `python3 jobs_scraping/scripts/orchestrator.py --apply <url>` to remove from pending_review and mark as applied

Valid statuses: Applied, Recruiter Screen, HM Screen, Technical Screen, Full Loop, Offer, Rejected, Ghosted, Withdrawn
