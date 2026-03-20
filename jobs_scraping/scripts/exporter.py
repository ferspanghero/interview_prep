import os
from datetime import date

HEADER = """# Active Jobs

| Company | Role | Salary | Location | AI | Source | Posted | Scraped | URL |
|---------|------|--------|----------|----|--------|--------|---------|-----|
"""


def _format_row(job):
    company = str(job.get("company") or "")
    ai_flag = "[AI]" if job.get("is_ai") else ""
    salary = job.get("salary") or "—"
    posted = job.get("posted") or "—"
    scraped = date.today().isoformat()
    url = f"[link]({job['url']})"

    return f"| {company} | {job['title']} | {salary} | {job['location']} | {ai_flag} | {job['source']} | {posted} | {scraped} | {url} |\n"


def append_jobs(jobs, active_path):
    if not jobs:
        return

    needs_header = not os.path.exists(active_path)

    if not needs_header:
        with open(active_path) as f:
            content = f.read()
        if "| Company |" not in content:
            needs_header = True

    # Read existing job lines
    existing_lines = []
    if not needs_header:
        with open(active_path) as f:
            for line in f:
                if line.startswith("| ") and not line.startswith("| Company") and not line.startswith("|---"):
                    existing_lines.append(line)

    # Add new job lines
    for job in jobs:
        existing_lines.append(_format_row(job))

    # Sort all job lines by company name
    existing_lines.sort(key=lambda l: l.split("|")[1].strip().lower())

    # Write header + sorted lines
    with open(active_path, "w") as f:
        f.write(HEADER)
        f.writelines(existing_lines)


def remove_jobs(urls, active_path):
    if not os.path.exists(active_path):
        return

    markers = {f"({url})" for url in urls}

    with open(active_path) as f:
        lines = f.readlines()

    with open(active_path, "w") as f:
        for line in lines:
            if any(m in line for m in markers):
                continue
            f.write(line)
