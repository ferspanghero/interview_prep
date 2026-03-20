# Interview Prep

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code)-powered framework for senior/staff-level software engineering interview preparation. Includes an AI interview coach, a real-time interview assistant, a coding problem tracker with solutions, and a job search aggregator tool.

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

A Python-based tool that scrapes job listings from multiple boards (Indeed, LinkedIn, Remotive, We Work Remotely), filters by criteria, deduplicates, and manages a pipeline from discovery to application. Includes Claude Code slash commands:

- `/search-jobs` — run the scraper and review new listings
- `/ignore-jobs` — mark listings to skip
- `/apply-to-job` — track applications
- `/enrich-salaries` — extract salary data from job descriptions

## Getting Started

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Python 3.10+ (for the job search tool)
- `python-jobspy` package (`pip install python-jobspy`)

### Setup

1. Fork this repo
2. Copy `myself.md.example` to `private/myself.md` and fill in your candidate background
3. Add your own cheatsheets in `private/cheatsheets/` (e.g., project-specific talking points, system design stories)
4. Add company-specific prep in `private/companies/` (e.g., behavioral question prep, coding question lists)
5. Add reference documents in `private/docs/` (e.g., resume, work summaries, design docs)
6. Customize job search location filters in `jobs_scraping/scripts/filters.py` and `jobs_scraping/scripts/scrapers/jobspy_scraper.py`

### Usage

Open the project directory with Claude Code:

```bash
cd interview_prep
claude
```

All interactions are routed through the `interview-coach` agent. Just start talking — coach mode is the default. Say **"assist mode"** for real-time interview help, **"coach mode"** to switch back.

## Project Structure

```
myself.md.example      # Template for private/myself.md — fill in your own background
private/               # Gitignored — your personal data
  myself.md            # Your candidate background (copy from myself.md.example)
  cheatsheets/         # All cheatsheets (coding tracker, solutions rubric, behavioral prep)
  companies/           # Your company-specific interview prep
  docs/                # Reference materials (resume, work summaries, design docs)
jobs_scraping/         # Job search aggregator tool
  scripts/             # Scraper, filter, exporter, salary enricher
  tests/               # Test suite
  listings/            # Gitignored — runtime data (scraped jobs, applications)
.claude/commands/      # Claude Code slash commands for job search workflow
```

## License

[MIT](LICENSE)
