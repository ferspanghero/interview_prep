import os
from exporter import append_jobs, remove_jobs


SAMPLE_JOBS = [
    {
        "title": "Senior Software Engineer",
        "company": "Stripe",
        "location": "Remote-CA",
        "salary": "$200K-$280K",
        "url": "https://stripe.com/jobs/1",
        "source": "Indeed",
        "posted": "2026-03-18",
        "is_ai": False,
    },
    {
        "title": "Staff SWE, AI Infra",
        "company": "Anthropic",
        "location": "Remote",
        "salary": "$250K-$350K",
        "url": "https://anthropic.com/jobs/1",
        "source": "Remotive",
        "posted": "2026-03-17",
        "is_ai": True,
    },
]


class TestAppendJobs:
    def test_creates_file_if_not_exists(self, tmp_path):
        active = str(tmp_path / "active_jobs.md")
        append_jobs(SAMPLE_JOBS, active)
        assert os.path.exists(active)

    def test_creates_header_on_new_file(self, tmp_path):
        active = str(tmp_path / "active_jobs.md")
        append_jobs(SAMPLE_JOBS, active)
        content = open(active).read()
        assert "# Active Jobs" in content
        assert "| Company |" in content

    def test_appends_all_jobs(self, tmp_path):
        active = str(tmp_path / "active_jobs.md")
        append_jobs(SAMPLE_JOBS, active)
        content = open(active).read()
        assert "Stripe" in content
        assert "Anthropic" in content

    def test_marks_ai_roles(self, tmp_path):
        active = str(tmp_path / "active_jobs.md")
        append_jobs(SAMPLE_JOBS, active)
        lines = open(active).readlines()
        anthropic_line = [l for l in lines if "Anthropic" in l][0]
        assert "[AI]" in anthropic_line

    def test_non_ai_role_no_flag(self, tmp_path):
        active = str(tmp_path / "active_jobs.md")
        append_jobs(SAMPLE_JOBS, active)
        lines = open(active).readlines()
        stripe_line = [l for l in lines if "Stripe" in l][0]
        assert "[AI]" not in stripe_line

    def test_appends_to_existing_file(self, tmp_path):
        active = str(tmp_path / "active_jobs.md")
        append_jobs([SAMPLE_JOBS[0]], active)
        append_jobs([SAMPLE_JOBS[1]], active)
        content = open(active).read()
        assert "Stripe" in content
        assert "Anthropic" in content

    def test_includes_scraped_date(self, tmp_path):
        active = str(tmp_path / "active_jobs.md")
        append_jobs(SAMPLE_JOBS, active)
        from datetime import date
        assert date.today().isoformat() in open(active).read()

    def test_includes_posted_date(self, tmp_path):
        active = str(tmp_path / "active_jobs.md")
        append_jobs(SAMPLE_JOBS, active)
        assert "2026-03-18" in open(active).read()

    def test_includes_url_as_link(self, tmp_path):
        active = str(tmp_path / "active_jobs.md")
        append_jobs(SAMPLE_JOBS, active)
        assert "[link](https://stripe.com/jobs/1)" in open(active).read()

    def test_no_header_duplication_on_append(self, tmp_path):
        active = str(tmp_path / "active_jobs.md")
        append_jobs([SAMPLE_JOBS[0]], active)
        append_jobs([SAMPLE_JOBS[1]], active)
        content = open(active).read()
        assert content.count("# Active Jobs") == 1
        assert content.count("| Company |") == 1

    def test_sorts_by_company(self, tmp_path):
        active = str(tmp_path / "active_jobs.md")
        append_jobs(SAMPLE_JOBS, active)
        lines = [l for l in open(active).readlines() if l.startswith("| ") and "Company" not in l and "---" not in l]
        companies = [l.split("|")[1].strip() for l in lines]
        assert companies == sorted(companies, key=str.lower)


class TestRemoveJobs:
    def test_removes_job_by_url(self, tmp_path):
        active = str(tmp_path / "active_jobs.md")
        append_jobs(SAMPLE_JOBS, active)
        remove_jobs(["https://stripe.com/jobs/1"], active)
        content = open(active).read()
        assert "Stripe" not in content
        assert "Anthropic" in content

    def test_removes_multiple_jobs(self, tmp_path):
        active = str(tmp_path / "active_jobs.md")
        append_jobs(SAMPLE_JOBS, active)
        remove_jobs(["https://stripe.com/jobs/1", "https://anthropic.com/jobs/1"], active)
        content = open(active).read()
        assert "Stripe" not in content
        assert "Anthropic" not in content

    def test_preserves_header(self, tmp_path):
        active = str(tmp_path / "active_jobs.md")
        append_jobs(SAMPLE_JOBS, active)
        remove_jobs(["https://stripe.com/jobs/1"], active)
        content = open(active).read()
        assert "# Active Jobs" in content
        assert "| Company |" in content

    def test_ignores_unknown_url(self, tmp_path):
        active = str(tmp_path / "active_jobs.md")
        append_jobs(SAMPLE_JOBS, active)
        remove_jobs(["https://unknown.com/jobs/1"], active)
        content = open(active).read()
        assert "Stripe" in content
        assert "Anthropic" in content

    def test_does_not_remove_similar_url(self, tmp_path):
        active = str(tmp_path / "active_jobs.md")
        append_jobs(SAMPLE_JOBS, active)
        remove_jobs(["https://stripe.com/jobs/1"], active)
        assert "Anthropic" in open(active).read()


class TestAppendJobsEmptyFile:
    def test_writes_header_to_empty_existing_file(self, tmp_path):
        active = str(tmp_path / "active_jobs.md")
        open(active, "w").close()
        append_jobs(SAMPLE_JOBS, active)
        content = open(active).read()
        assert "# Active Jobs" in content
        assert "Stripe" in content

    def test_writes_header_after_all_jobs_removed(self, tmp_path):
        active = str(tmp_path / "active_jobs.md")
        append_jobs(SAMPLE_JOBS, active)
        remove_jobs(["https://stripe.com/jobs/1", "https://anthropic.com/jobs/1"], active)
        append_jobs(SAMPLE_JOBS, active)
        content = open(active).read()
        assert content.count("| Company |") == 1
        assert "Stripe" in content
