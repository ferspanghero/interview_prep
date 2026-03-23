import json, os
from unittest.mock import patch
from orchestrator import search, ignore, apply
from exporter import append_jobs


MOCK_JOBS_SOURCE_A = [
    {
        "title": "Senior Software Engineer",
        "company": "Stripe",
        "location": "Remote",
        "salary": "$200K-$280K",
        "url": "https://stripe.com/jobs/1",
        "source": "Indeed",
        "posted": "2026-03-18",
    },
]

MOCK_JOBS_SOURCE_B = [
    {
        "title": "Staff SWE, AI Infra",
        "company": "Anthropic",
        "location": "Remote",
        "salary": "$250K-$350K",
        "url": "https://anthropic.com/jobs/1",
        "source": "Remotive",
        "posted": "2026-03-17",
    },
]


class TestOrchestratorSearch:
    @patch("scrapers.jobspy_scraper.fetch")
    @patch("scrapers.remotive.fetch")
    @patch("scrapers.wwr.fetch")
    def test_aggregates_from_all_sources(self, mock_wwr, mock_remotive, mock_jobspy_scraper, tmp_path):
        mock_jobspy_scraper.return_value = MOCK_JOBS_SOURCE_A
        mock_remotive.return_value = MOCK_JOBS_SOURCE_B
        mock_wwr.return_value = []
        new_jobs = search(
            pending_path=str(tmp_path / "pending_review.md"),
            scraped_path=str(tmp_path / "already_scraped.json"),
            ignore_path=str(tmp_path / "ignored.json"),
            applied_path=str(tmp_path / "applied.json"),
        )
        assert len(new_jobs) == 2

    @patch("scrapers.jobspy_scraper.fetch")
    @patch("scrapers.remotive.fetch")
    @patch("scrapers.wwr.fetch")
    def test_deduplicates_already_scraped(self, mock_wwr, mock_remotive, mock_jobspy_scraper, tmp_path):
        mock_jobspy_scraper.return_value = MOCK_JOBS_SOURCE_A
        mock_remotive.return_value = []
        mock_wwr.return_value = []
        scraped_path = str(tmp_path / "already_scraped.json")
        with open(scraped_path, "w") as f:
            json.dump(["https://stripe.com/jobs/1"], f)
        new_jobs = search(
            pending_path=str(tmp_path / "pending_review.md"),
            scraped_path=scraped_path,
            ignore_path=str(tmp_path / "ignored.json"),
            applied_path=str(tmp_path / "applied.json"),
        )
        assert len(new_jobs) == 0

    @patch("scrapers.jobspy_scraper.fetch")
    @patch("scrapers.remotive.fetch")
    @patch("scrapers.wwr.fetch")
    def test_deduplicates_ignored(self, mock_wwr, mock_remotive, mock_jobspy_scraper, tmp_path):
        mock_jobspy_scraper.return_value = MOCK_JOBS_SOURCE_A
        mock_remotive.return_value = []
        mock_wwr.return_value = []
        ignore_path = str(tmp_path / "ignored.json")
        with open(ignore_path, "w") as f:
            json.dump(["https://stripe.com/jobs/1"], f)
        new_jobs = search(
            pending_path=str(tmp_path / "pending_review.md"),
            scraped_path=str(tmp_path / "already_scraped.json"),
            ignore_path=ignore_path,
            applied_path=str(tmp_path / "applied.json"),
        )
        assert len(new_jobs) == 0

    @patch("scrapers.jobspy_scraper.fetch")
    @patch("scrapers.remotive.fetch")
    @patch("scrapers.wwr.fetch")
    def test_deduplicates_applied(self, mock_wwr, mock_remotive, mock_jobspy_scraper, tmp_path):
        mock_jobspy_scraper.return_value = MOCK_JOBS_SOURCE_A
        mock_remotive.return_value = []
        mock_wwr.return_value = []
        applied_path = str(tmp_path / "applied.json")
        with open(applied_path, "w") as f:
            json.dump(["https://stripe.com/jobs/1"], f)
        new_jobs = search(
            pending_path=str(tmp_path / "pending_review.md"),
            scraped_path=str(tmp_path / "already_scraped.json"),
            ignore_path=str(tmp_path / "ignored.json"),
            applied_path=applied_path,
        )
        assert len(new_jobs) == 0

    @patch("scrapers.jobspy_scraper.fetch")
    @patch("scrapers.remotive.fetch")
    @patch("scrapers.wwr.fetch")
    def test_filters_out_low_salary(self, mock_wwr, mock_remotive, mock_jobspy_scraper, tmp_path):
        mock_jobspy_scraper.return_value = [{
            "title": "Senior Software Engineer",
            "company": "LowPay Corp",
            "location": "Remote",
            "salary": "$120,000 - $150,000",
            "url": "https://lowpay.com/jobs/1",
            "source": "Indeed",
            "posted": "2026-03-18",
            "description": "",
        }]
        mock_remotive.return_value = []
        mock_wwr.return_value = []
        new_jobs = search(
            pending_path=str(tmp_path / "pending_review.md"),
            scraped_path=str(tmp_path / "already_scraped.json"),
            ignore_path=str(tmp_path / "ignored.json"),
            applied_path=str(tmp_path / "applied.json"),
        )
        assert len(new_jobs) == 0

    @patch("scrapers.jobspy_scraper.fetch")
    @patch("scrapers.remotive.fetch")
    @patch("scrapers.wwr.fetch")
    def test_keeps_job_without_salary(self, mock_wwr, mock_remotive, mock_jobspy_scraper, tmp_path):
        mock_jobspy_scraper.return_value = [{
            "title": "Senior Software Engineer",
            "company": "NoSalary Inc",
            "location": "Remote",
            "salary": None,
            "url": "https://nosalary.com/jobs/1",
            "source": "Indeed",
            "posted": "2026-03-18",
            "description": "",
        }]
        mock_remotive.return_value = []
        mock_wwr.return_value = []
        new_jobs = search(
            pending_path=str(tmp_path / "pending_review.md"),
            scraped_path=str(tmp_path / "already_scraped.json"),
            ignore_path=str(tmp_path / "ignored.json"),
            applied_path=str(tmp_path / "applied.json"),
        )
        assert len(new_jobs) == 1

    @patch("scrapers.jobspy_scraper.fetch")
    @patch("scrapers.remotive.fetch")
    @patch("scrapers.wwr.fetch")
    def test_updates_already_scraped(self, mock_wwr, mock_remotive, mock_jobspy_scraper, tmp_path):
        mock_jobspy_scraper.return_value = MOCK_JOBS_SOURCE_A
        mock_remotive.return_value = []
        mock_wwr.return_value = []
        scraped_path = str(tmp_path / "already_scraped.json")
        search(
            pending_path=str(tmp_path / "pending_review.md"),
            scraped_path=scraped_path,
            ignore_path=str(tmp_path / "ignored.json"),
            applied_path=str(tmp_path / "applied.json"),
        )
        with open(scraped_path) as f:
            scraped = json.load(f)
        assert "https://stripe.com/jobs/1" in scraped


class TestOrchestratorIgnore:
    def test_adds_to_ignored_json(self, tmp_path):
        pending = str(tmp_path / "pending_review.md")
        ignore_path = str(tmp_path / "ignored.json")
        scraped_path = str(tmp_path / "already_scraped.json")
        append_jobs(
            [{"title": "Senior SWE", "company": "Stripe", "location": "Remote",
              "salary": "$200K", "url": "https://stripe.com/jobs/1", "source": "Indeed",
              "posted": "2026-03-18", "is_ai": False}],
            pending,
        )
        with open(scraped_path, "w") as f:
            json.dump(["https://stripe.com/jobs/1"], f)
        ignore(urls=["https://stripe.com/jobs/1"], pending_path=pending, ignore_path=ignore_path, scraped_path=scraped_path)
        with open(ignore_path) as f:
            ignored = json.load(f)
        assert "https://stripe.com/jobs/1" in ignored

    def test_removes_from_pending(self, tmp_path):
        pending = str(tmp_path / "pending_review.md")
        append_jobs(
            [{"title": "Senior SWE", "company": "Stripe", "location": "Remote",
              "salary": "$200K", "url": "https://stripe.com/jobs/1", "source": "Indeed",
              "posted": "2026-03-18", "is_ai": False}],
            pending,
        )
        with open(str(tmp_path / "already_scraped.json"), "w") as f:
            json.dump(["https://stripe.com/jobs/1"], f)
        ignore(urls=["https://stripe.com/jobs/1"], pending_path=pending, ignore_path=str(tmp_path / "ignored.json"), scraped_path=str(tmp_path / "already_scraped.json"))
        assert "Stripe" not in open(pending).read()

    def test_removes_from_already_scraped(self, tmp_path):
        pending = str(tmp_path / "pending_review.md")
        scraped_path = str(tmp_path / "already_scraped.json")
        append_jobs(
            [{"title": "Senior SWE", "company": "Stripe", "location": "Remote",
              "salary": "$200K", "url": "https://stripe.com/jobs/1", "source": "Indeed",
              "posted": "2026-03-18", "is_ai": False}],
            pending,
        )
        with open(scraped_path, "w") as f:
            json.dump(["https://stripe.com/jobs/1"], f)
        ignore(urls=["https://stripe.com/jobs/1"], pending_path=pending, ignore_path=str(tmp_path / "ignored.json"), scraped_path=scraped_path)
        with open(scraped_path) as f:
            scraped = json.load(f)
        assert "https://stripe.com/jobs/1" not in scraped

    def test_deduplicates_ignore_list(self, tmp_path):
        pending = str(tmp_path / "pending_review.md")
        ignore_path = str(tmp_path / "ignored.json")
        scraped_path = str(tmp_path / "already_scraped.json")
        append_jobs(
            [{"title": "Senior SWE", "company": "Stripe", "location": "Remote",
              "salary": "$200K", "url": "https://stripe.com/jobs/1", "source": "Indeed",
              "posted": "2026-03-18", "is_ai": False}],
            pending,
        )
        with open(scraped_path, "w") as f:
            json.dump(["https://stripe.com/jobs/1"], f)
        ignore(urls=["https://stripe.com/jobs/1"], pending_path=pending, ignore_path=ignore_path, scraped_path=scraped_path)
        ignore(urls=["https://stripe.com/jobs/1"], pending_path=pending, ignore_path=ignore_path, scraped_path=scraped_path)
        with open(ignore_path) as f:
            ignored = json.load(f)
        assert ignored.count("https://stripe.com/jobs/1") == 1


class TestOrchestratorApply:
    def test_adds_url_to_applied_json(self, tmp_path):
        pending = str(tmp_path / "pending_review.md")
        applied_path = str(tmp_path / "applied.json")
        append_jobs(
            [{"title": "Senior SWE", "company": "Stripe", "location": "Remote",
              "salary": "$200K", "url": "https://stripe.com/jobs/1", "source": "Indeed",
              "posted": "2026-03-18", "is_ai": False}],
            pending,
        )
        apply(url="https://stripe.com/jobs/1", pending_path=pending, applied_path=applied_path)
        with open(applied_path) as f:
            applied = json.load(f)
        assert "https://stripe.com/jobs/1" in applied

    def test_removes_from_pending(self, tmp_path):
        pending = str(tmp_path / "pending_review.md")
        applied_path = str(tmp_path / "applied.json")
        append_jobs(
            [{"title": "Senior SWE", "company": "Stripe", "location": "Remote",
              "salary": "$200K", "url": "https://stripe.com/jobs/1", "source": "Indeed",
              "posted": "2026-03-18", "is_ai": False}],
            pending,
        )
        apply(url="https://stripe.com/jobs/1", pending_path=pending, applied_path=applied_path)
        assert "Stripe" not in open(pending).read()

    def test_deduplicates_applied_list(self, tmp_path):
        pending = str(tmp_path / "pending_review.md")
        applied_path = str(tmp_path / "applied.json")
        apply(url="https://stripe.com/jobs/1", pending_path=pending, applied_path=applied_path)
        apply(url="https://stripe.com/jobs/1", pending_path=pending, applied_path=applied_path)
        with open(applied_path) as f:
            applied = json.load(f)
        assert applied.count("https://stripe.com/jobs/1") == 1

    def test_trailing_slash_still_removes_from_pending(self, tmp_path):
        pending = str(tmp_path / "pending_review.md")
        applied_path = str(tmp_path / "applied.json")
        append_jobs(
            [{"title": "Senior SWE", "company": "Stripe", "location": "Remote",
              "salary": "$200K", "url": "https://stripe.com/jobs/1", "source": "Indeed",
              "posted": "2026-03-18", "is_ai": False}],
            pending,
        )
        apply(url="https://stripe.com/jobs/1/", pending_path=pending, applied_path=applied_path)
        assert "Stripe" not in open(pending).read()

    def test_trailing_slash_normalized_in_applied_json(self, tmp_path):
        pending = str(tmp_path / "pending_review.md")
        applied_path = str(tmp_path / "applied.json")
        apply(url="https://stripe.com/jobs/1/", pending_path=pending, applied_path=applied_path)
        with open(applied_path) as f:
            applied = json.load(f)
        assert "https://stripe.com/jobs/1" in applied
        assert "https://stripe.com/jobs/1/" not in applied
