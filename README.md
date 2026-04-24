# Interview Prep

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code)-powered framework for software engineering interview prep — AI coach, real-time interview assistant, and automated job search pipeline.

## Features

### AI Interview Coach (Coach Mode)

Claude Code acts as your interviewer and coach, with support for:

- **Behavioral prep** — drills questions, critiques answers, enforces STAR format
- **System design** — staff-level system design mocks with structured feedback
- **Coding discussion** — think through problems, pressure-test approaches
- **Mock interviews** — full 45-minute simulated interviews
- **Story bank** — build and refine career stories tagged by theme
- **Role research** — research specific companies/roles and build targeted prep plans

### Real-Time Interview Assistant (Assist Mode)

For live interviews that allow AI assistance. Say **"assist mode"** to switch. Claude gives direct, fast answers:

- Coding: bullet-point tips + full solution code
- Behavioral: drafts STAR answers from your story bank
- System design: architectural recommendations from your experience

### Coding Problem Tracker

- `private/cheatsheets/coding_questions.md` — master list of problems with status and tips
- `private/cheatsheets/coding_rubric.md` — solutions with consistent style patterns and complexity analysis

### Job Search Aggregator

A Python-based tool that scrapes job listings from multiple boards (Indeed, LinkedIn, Remotive, We Work Remotely), filters by criteria, deduplicates, and manages a pipeline from discovery to application.

All runtime data lives in `jobs_scraping/listings/` (gitignored):

| File | Purpose |
|------|---------|
| `pending_review.md` | Jobs awaiting your review |
| `applications.md` | Tracked applications with comp, status, and next steps |
| `companies.json` | Cached company ratings, blocklist, and notes |
| `applied.json` | URLs marked as applied (dedup) |
| `ignored.json` | URLs marked as ignored (dedup) |
| `already_scraped.json` | URLs already seen by the scraper (dedup) |

#### Core workflow

These commands run the main search-review-apply loop:

- **`/search-jobs`** — scrape new listings from all job boards → adds to `pending_review.md`, updates `already_scraped.json`. Supports flags: `--source jobspy|remotive|wwr`, `--limit N`, `--hours_old N` (default: 168 = 7 days)
- **`/ignore-jobs`** — dismiss listings you're not interested in (e.g., `/ignore-jobs scribd, narvar`). Optionally block the company to filter them from future searches (e.g., `/ignore-jobs giga, block_company`) → removes from `pending_review.md`, adds to `ignored.json`, optionally updates blocklist in `companies.json`
- **`/block-companies`** — block companies from appearing in future searches (e.g., `/block-companies giga, omnissa`) → updates blocklist in `companies.json`
- **`/apply-to-job`** — track an application with comp, status, and next steps (e.g., `/apply-to-job https://linkedin.com/jobs/view/123`) → appends to `applications.md`, removes from `pending_review.md`, adds to `applied.json`

#### On-demand enrichment

These commands are token-intensive (they make many web requests), so they run separately rather than on every search:

- **`/enrich-salaries`** — fetch salary data for listings missing compensation info by scraping job posting URLs → updates salary column in `pending_review.md`
- **`/research-companies`** — look up Glassdoor and Blind ratings for all companies in `pending_review.md` → updates `companies.json` (cached, repeat runs only fetch new companies)

#### Interview prep

- **`/prep-company`** — research a company's interview process and generate a prep package from a job listing URL (e.g., `/prep-company https://linkedin.com/jobs/view/123`) → creates `private/companies/<company>/` with `prep_overview.md`, `frequent_coding_questions.md`, `frequent_behavioral_questions.md`, and `frequent_system_design_questions.md`

## Getting Started

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Python 3.10+ (for the job search tool)
- `python-jobspy` package (`pip install python-jobspy`)

### Setup

1. Fork this repo
2. Copy `myself.md.example` to `private/myself.md` and fill in your candidate background — **the interview coach reads this file to tailor all coaching, mocks, and feedback to your experience**
3. (Optional) Copy `interview_feedback.md.example` to `private/interview_feedback.md` to log feedback from past interviews — the coach uses this to drill against recurring weaknesses
4. Add your own cheatsheets in `private/cheatsheets/` (e.g., coding rubric, project-specific talking points, system design stories)
5. Add company-specific prep in `private/companies/` (e.g., behavioral question prep, coding question lists)
6. Add reference documents in `private/docs/` (e.g., resume, work summaries, design docs) — the more context you provide (work summaries, design docs, performance reviews), the better the coach can help craft behavioral answers grounded in your real experience
7. Customize job search location filters in `jobs_scraping/scripts/filters.py` and `jobs_scraping/scripts/scrapers/jobspy_scraper.py`

### Usage

Open the project directory with Claude Code:

```bash
cd interview_prep
claude
```

All interactions are routed through the `interview-coach` agent. Just start talking — coach mode is the default. Say **"assist mode"** for real-time interview help, **"coach mode"** to switch back.

## Project Structure

```
myself.md.example              # Template for private/myself.md — fill in your own background
interview_feedback.md.example  # Template for private/interview_feedback.md — log interview feedback
private/                       # Gitignored — your personal data
  myself.md                    # Your candidate background (copy from myself.md.example)
  interview_feedback.md        # Feedback from past interviews (copy from interview_feedback.md.example)
  cheatsheets/                 # Rehearsal-ready cheatsheets (coding, system design, behavioral, probing-question playbooks)
  companies/                   # Company-specific interview prep (created by /prep-company)
  docs/                        # Reference materials (resume, work summaries, design docs)
jobs_scraping/           # Job search aggregator tool
  scripts/               # Scraper, filter, exporter, salary enricher
  tests/                 # Test suite
  listings/              # Gitignored — see data files table above
.claude/commands/        # Claude Code slash commands
.claude/agents/          # Interview coach agent definition
```

## License

[MIT](LICENSE)
