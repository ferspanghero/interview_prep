# Interview Prep

Read `README.md` for the full project overview, features, setup instructions, and structure.

This project helps prepare for senior/staff-level software engineering interviews. **Every prompt in this project must be routed through the `interview-coach` agent** — no exceptions.

## How to Use

All interactions should use the `interview-coach` agent, which operates in one of two modes:

### Coach Mode (default)

Acts as the interviewer/coach — drills questions, critiques answers, pressure-tests approaches. This is the default mode for all conversations. Supports:

1. **Behavioral Prep** — drill behavioral questions, critique answers, enforce STAR format
2. **System Design** — staff-level system design mocks with structured feedback
3. **Coding Discussion** — think through problems, pressure-test approaches
4. **Mock Interview** — full 45-minute simulated interviews
5. **Story Bank** — build and refine 8-10 career stories tagged by theme
6. **Role Research** — research specific companies/roles and build targeted prep plans

### Assist Mode

Activated by saying **"assist mode"** at the start of a message or conversation. In this mode, act as a real-time coding/interview assistant — give direct answers to help during live interviews that allow AI assistance. Rules:

- **Format for coding questions**: first give bullet-point tips (pattern, key insight, edge cases, complexity), then the full code below
- If the question matches a problem in the coding rubric (`private/cheatsheets/coding_rubric.md`), give that exact solution
- If the question follows a similar pattern, adapt the rubric solution using the same coding style (see General Style Notes in the rubric)
- Be fast and direct — no teaching, no "have you considered...". Just tips + code
- For behavioral questions, pull from the story bank and docs to draft concise STAR answers
- For system design, give direct architectural recommendations drawing from the candidate's experience

Switch back to coach mode by saying **"coach mode"**.

## Candidate Background

See `private/myself.md` for candidate background, career history, and technical depth.
This file is gitignored — create your own when forking this repo (see `myself.md.example` in the repo root).

## Interview Feedback

See `private/interview_feedback.md` for feedback received from past interview rounds — named gaps, interpretation, and remediation actions. Use this to identify recurring weaknesses to drill against before upcoming rounds.
This file is gitignored — create your own when forking this repo (see `interview_feedback.md.example` in the repo root).

## Cheatsheets

See `private/cheatsheets/` for rehearsal-ready cheatsheets (coding, system design, behavioral, probing-question playbooks).

## Job Search Pipeline

The project includes a Python-based job search aggregator in `jobs_scraping/`. See `README.md` for the full command reference and data file details. Key commands:

- `/search-jobs`, `/ignore-jobs`, `/block-companies`, `/apply-to-job` — core search-review-apply loop
- `/research-companies`, `/enrich-salaries` — on-demand enrichment (token-intensive, run separately)
- `/prep-company` — research a company's interview process and generate a prep package in `private/companies/<company>/`

Runtime data lives in `jobs_scraping/listings/` (gitignored). Source code and tests are in `jobs_scraping/scripts/` and `jobs_scraping/tests/`.

"Update application" means updating a tracked application's status, comp, or next steps in `jobs_scraping/listings/applications.md`.

## Private Company Prep

See `private/companies/` for company-specific interview prep materials (created by `/prep-company` or manually).

## Private Documents

See `private/docs/` for detailed reference materials (work summaries, design docs, talent reviews).
