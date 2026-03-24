Build an interview prep package for a specific company: $ARGUMENTS

The user provides a job listing URL (e.g., `/prep-company https://linkedin.com/jobs/view/123`). Fetch the posting to extract the company name, role title, level, and requirements.

## Step 1: Check for existing prep

Look in `private/companies/` for an existing directory matching the company name. If found, display what's already there and ask if the user wants to update or start fresh.

## Step 2: Research the company's interview process

Use WebSearch to find recent (last 12 months) interview experiences for this company and level. Search for:
- `"[company] [level] software engineer interview experience"` on Glassdoor, Blind, LeetCode Discuss, Levels.fyi
- `"[company] interview process software engineer"` for official process descriptions
- `"[company] coding interview questions"` for reported problems

Synthesize findings into actionable prep — not a link dump.

## Step 3: Create prep files

Create a directory `private/companies/[company]/` with these files:

### prep_overview.md

1. **Header**: Company, role, interview date (if known from `jobs_scraping/listings/applications.md`), format
2. **Interview framing**: What this company evaluates — their values/principles and how to frame answers accordingly. If the candidate has a background file at `private/myself.md`, include a translation guide mapping their experience to the company's evaluation criteria.
3. **Interview process**: Full pipeline with stages, format, duration, and focus for each round
4. **Behavioral questions to practice**: Sourced from candidate reports. If `private/myself.md` exists, map questions to the candidate's stories.
5. **Technical focus areas**: Patterns, topics, and system design themes reported for this company and level
6. **Prep timeline**: If an interview date is known, a day-by-day prep plan leading up to it

### frequent_coding_questions.md

Coding problems reported at this company and level, organized by priority tier:
- **Tier 1**: Confirmed at this level, high frequency across multiple reports
- **Tier 2**: Confirmed at adjacent levels or moderate frequency
- **Tier 3**: Reported but lower confidence

Table format with: LC number, problem name, difficulty, pattern, reported follow-ups, and status checkbox.
If the candidate has a coding rubric at `private/cheatsheets/coding_rubric.md`, cross-reference to mark problems they've already solved.

### frequent_behavioral_questions.md (if the process includes behavioral rounds)

Common behavioral questions for this company, with:
- The question
- Company-specific framing tips (e.g., growth mindset signals, collaboration emphasis, leadership principles)
- If `private/myself.md` exists, suggest which candidate story maps best to each question

## Step 4: Summary

Display a summary of what was created and recommend which interview-coach modes (behavioral, system design, coding) to focus on based on the process.
