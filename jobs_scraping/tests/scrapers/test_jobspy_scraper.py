from unittest.mock import patch
import pandas as pd


MOCK_INDEED_DATA = pd.DataFrame([
    {
        "site": "indeed",
        "title": "Senior Software Engineer",
        "company": "Stripe",
        "location": "Vancouver, BC, CA",
        "job_url": "https://ca.indeed.com/viewjob?jk=abc123",
        "job_url_direct": "https://jobs.lever.co/stripe/abc123",
        "date_posted": "2026-03-18",
        "min_amount": 200000.0,
        "max_amount": 280000.0,
        "currency": "CAD",
        "is_remote": True,
        "description": "Building payment infrastructure",
    },
])

MOCK_LINKEDIN_DATA = pd.DataFrame([
    {
        "site": "linkedin",
        "title": "Staff Backend Engineer",
        "company": "Databricks",
        "location": "Vancouver, British Columbia, Canada",
        "job_url": "https://www.linkedin.com/jobs/view/12345",
        "job_url_direct": None,
        "date_posted": "2026-03-17",
        "min_amount": None,
        "max_amount": None,
        "currency": None,
        "is_remote": False,
        "description": "AI platform engineer working on ML pipelines",
    },
])

MOCK_LINKEDIN_WITH_SALARY_IN_DESC = pd.DataFrame([
    {
        "site": "linkedin",
        "title": "Senior Software Engineer",
        "company": "Grafana Labs",
        "location": "Vancouver, British Columbia, Canada",
        "job_url": "https://www.linkedin.com/jobs/view/67890",
        "job_url_direct": None,
        "date_posted": "2026-03-20",
        "min_amount": None,
        "max_amount": None,
        "currency": None,
        "is_remote": False,
        "description": "The compensation range for this role is $186,368 - $223,642 CAD.",
    },
])

MOCK_INDEED_WITH_PIPE = pd.DataFrame([
    {
        "site": "indeed",
        "title": "Staff Software Engineer - Grafana Cloud k6 | Canada | Remote",
        "company": "Grafana Labs",
        "location": "Remote, CA",
        "job_url": "https://ca.indeed.com/viewjob?jk=grafana303",
        "job_url_direct": "https://grafana.com/careers/grafana303",
        "date_posted": "2026-02-24",
        "min_amount": None,
        "max_amount": None,
        "currency": None,
        "is_remote": True,
        "description": "Build observability tools at scale.",
    },
])

EMPTY_DF = pd.DataFrame()


def _mock_scrape_factory(indeed_data=EMPTY_DF, linkedin_data=EMPTY_DF):
    """Returns a side_effect function that returns different data per site_name."""
    def _scrape(**kwargs):
        site = kwargs.get("site_name", [""])[0]
        if site == "indeed":
            return indeed_data
        elif site == "linkedin":
            return linkedin_data
        return EMPTY_DF
    return _scrape


class TestJobspyFetch:
    @patch("jobspy_scraper.scrape_jobs")
    def test_returns_list(self, mock_scrape):
        mock_scrape.side_effect = _mock_scrape_factory(indeed_data=MOCK_INDEED_DATA)
        from jobspy_scraper import fetch
        jobs = fetch()
        assert isinstance(jobs, list)

    @patch("jobspy_scraper.scrape_jobs")
    def test_jobs_have_required_fields(self, mock_scrape):
        mock_scrape.side_effect = _mock_scrape_factory(indeed_data=MOCK_INDEED_DATA, linkedin_data=MOCK_LINKEDIN_DATA)
        from jobspy_scraper import fetch
        jobs = fetch()
        required = {"title", "company", "location", "salary", "url", "source", "posted"}
        for job in jobs:
            assert required.issubset(job.keys()), f"Missing fields: {required - job.keys()}"

    @patch("jobspy_scraper.scrape_jobs")
    def test_returns_jobs_from_both_sources(self, mock_scrape):
        mock_scrape.side_effect = _mock_scrape_factory(indeed_data=MOCK_INDEED_DATA, linkedin_data=MOCK_LINKEDIN_DATA)
        from jobspy_scraper import fetch
        jobs = fetch()
        sources = {j["source"] for j in jobs}
        assert "Indeed" in sources
        assert "LinkedIn" in sources

    @patch("jobspy_scraper.scrape_jobs")
    def test_indeed_source_attribution(self, mock_scrape):
        mock_scrape.side_effect = _mock_scrape_factory(indeed_data=MOCK_INDEED_DATA)
        from jobspy_scraper import fetch
        jobs = fetch()
        stripe_jobs = [j for j in jobs if j["company"] == "Stripe"]
        assert len(stripe_jobs) > 0
        assert stripe_jobs[0]["source"] == "Indeed"

    @patch("jobspy_scraper.scrape_jobs")
    def test_linkedin_source_attribution(self, mock_scrape):
        mock_scrape.side_effect = _mock_scrape_factory(linkedin_data=MOCK_LINKEDIN_DATA)
        from jobspy_scraper import fetch
        jobs = fetch()
        db_jobs = [j for j in jobs if j["company"] == "Databricks"]
        assert len(db_jobs) > 0
        assert db_jobs[0]["source"] == "LinkedIn"

    @patch("jobspy_scraper.scrape_jobs")
    def test_salary_extracted_from_description(self, mock_scrape):
        """Salary comes from description enrichment, not structured fields."""
        data = pd.DataFrame([{
            "site": "indeed",
            "title": "Senior Software Engineer",
            "company": "Stripe",
            "location": "Vancouver, BC, CA",
            "job_url": "https://ca.indeed.com/viewjob?jk=abc123",
            "job_url_direct": "https://jobs.lever.co/stripe/abc123",
            "date_posted": "2026-03-18",
            "min_amount": 200000.0,
            "max_amount": 280000.0,
            "currency": "USD",
            "is_remote": True,
            "description": "Base salary range: $200,000 - $280,000 CAD",
        }])
        mock_scrape.side_effect = _mock_scrape_factory(indeed_data=data)
        from jobspy_scraper import fetch
        jobs = fetch()
        stripe_job = [j for j in jobs if j["company"] == "Stripe"][0]
        assert stripe_job["salary"] is not None
        assert "CAD" in stripe_job["salary"]
        assert "USD" not in stripe_job["salary"]

    @patch("jobspy_scraper.scrape_jobs")
    def test_missing_salary_is_none(self, mock_scrape):
        mock_scrape.side_effect = _mock_scrape_factory(linkedin_data=MOCK_LINKEDIN_DATA)
        from jobspy_scraper import fetch
        jobs = fetch()
        db_job = [j for j in jobs if j["company"] == "Databricks"][0]
        assert db_job["salary"] is None

    @patch("jobspy_scraper.scrape_jobs")
    def test_extracts_salary_from_description(self, mock_scrape):
        mock_scrape.side_effect = _mock_scrape_factory(linkedin_data=MOCK_LINKEDIN_WITH_SALARY_IN_DESC)
        from jobspy_scraper import fetch
        jobs = fetch()
        grafana_job = [j for j in jobs if j["company"] == "Grafana Labs"][0]
        assert grafana_job["salary"] is not None
        assert "186,368" in grafana_job["salary"]

    @patch("jobspy_scraper.scrape_jobs")
    def test_replaces_nan_company_with_unknown(self, mock_scrape):
        data = pd.DataFrame([{
            "site": "indeed",
            "title": "Senior Software Engineer",
            "company": float("nan"),
            "location": "Remote, CA",
            "job_url": "https://ca.indeed.com/viewjob?jk=nan999",
            "date_posted": "2026-03-15",
            "min_amount": None,
            "max_amount": None,
            "currency": None,
            "is_remote": True,
            "description": "Some job",
        }])
        mock_scrape.side_effect = _mock_scrape_factory(indeed_data=data)
        from jobspy_scraper import fetch
        jobs = fetch()
        assert len(jobs) >= 1
        nan_job = [j for j in jobs if j["url"] == "https://ca.indeed.com/viewjob?jk=nan999"][0]
        assert nan_job["company"] == "Unknown"

    @patch("jobspy_scraper.scrape_jobs")
    def test_strips_pipe_suffixes_from_title(self, mock_scrape):
        mock_scrape.side_effect = _mock_scrape_factory(indeed_data=MOCK_INDEED_WITH_PIPE)
        from jobspy_scraper import fetch
        jobs = fetch()
        grafana_job = [j for j in jobs if j["company"] == "Grafana Labs"][0]
        assert "|" not in grafana_job["title"]
        assert "Grafana Cloud k6" in grafana_job["title"]

    @patch("jobspy_scraper.scrape_jobs")
    def test_uses_direct_url_when_available(self, mock_scrape):
        mock_scrape.side_effect = _mock_scrape_factory(indeed_data=MOCK_INDEED_DATA)
        from jobspy_scraper import fetch
        jobs = fetch()
        stripe_job = [j for j in jobs if j["company"] == "Stripe"][0]
        assert "lever.co" in stripe_job["url"]
        assert "indeed.com" not in stripe_job["url"]

    @patch("jobspy_scraper.scrape_jobs")
    def test_linkedin_falls_back_to_job_url(self, mock_scrape):
        mock_scrape.side_effect = _mock_scrape_factory(linkedin_data=MOCK_LINKEDIN_DATA)
        from jobspy_scraper import fetch
        jobs = fetch()
        db_job = [j for j in jobs if j["company"] == "Databricks"][0]
        assert "linkedin.com" in db_job["url"]

    @patch("jobspy_scraper.scrape_jobs")
    def test_deduplicates_across_searches(self, mock_scrape):
        mock_scrape.side_effect = _mock_scrape_factory(indeed_data=MOCK_INDEED_DATA, linkedin_data=MOCK_LINKEDIN_DATA)
        from jobspy_scraper import fetch
        jobs = fetch()
        urls = [j["url"] for j in jobs]
        assert len(urls) == len(set(urls))

    @patch("jobspy_scraper.scrape_jobs")
    def test_logs_error_on_scrape_failure(self, mock_scrape, caplog):
        mock_scrape.side_effect = Exception("API down")
        from jobspy_scraper import fetch
        import logging
        with caplog.at_level(logging.ERROR):
            jobs = fetch()
        assert len(jobs) == 0
        assert "API down" in caplog.text
