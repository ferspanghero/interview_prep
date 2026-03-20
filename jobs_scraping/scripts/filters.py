import re

from salary_enricher import extract_numbers

TITLE_PATTERN = re.compile(
    r"(senior|staff|lead|principal).*(software|backend|platform|swe|fullstack|full.stack)",
    re.IGNORECASE,
)

LOCATION_PATTERN = re.compile(
    r"(vancouver|british columbia|\bbc\b|worldwide|anywhere)",
    re.IGNORECASE,
)

REMOTE_US_ONLY_PATTERN = re.compile(
    r"remote\s*[\(\-]\s*us\s*\)?$",
    re.IGNORECASE,
)

EXCLUDE_PATTERN = re.compile(
    r"\b(junior|intern|manager|director|contractor|contract)\b",
    re.IGNORECASE,
)

AI_PATTERN = re.compile(
    r"\b(ai|ml|llm|agent|rag|nlp|machine.learning|artificial.intelligence)\b",
    re.IGNORECASE,
)


def matches_title(title):
    if not title:
        return False
    return bool(TITLE_PATTERN.search(title))


def matches_location(location):
    if not location:
        return False
    if REMOTE_US_ONLY_PATTERN.search(location):
        return False
    if LOCATION_PATTERN.search(location):
        return True
    if re.search(r"\bremote\b", location, re.IGNORECASE):
        return True
    return False


def is_excluded(title):
    if not title:
        return False
    return bool(EXCLUDE_PATTERN.search(title))


def is_ai_role(title, description=""):
    text = f"{title} {description or ''}"
    return bool(AI_PATTERN.search(text))


def matches_salary(salary, min_annual=200000):
    """Return True if salary meets the minimum threshold.

    Keeps jobs with no salary data (None, empty, "—") and jobs with
    hourly/monthly rates (need conversion context). Only rejects annual
    salaries where the max value is below min_annual.
    """
    if not salary or salary == "—":
        return True
    # Keep hourly/monthly rates — they need conversion context we don't have.
    # All other formats are treated as annual.
    if re.search(r'/hr|per hour|per month|/month', salary, re.IGNORECASE):
        return True
    nums = extract_numbers(salary)
    if not nums:
        return True
    return max(nums) >= min_annual
