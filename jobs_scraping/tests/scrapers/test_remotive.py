import os
from unittest.mock import patch, MagicMock

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures")


def load_fixture(name):
    with open(os.path.join(FIXTURE_DIR, name)) as f:
        return f.read()


class TestRemotiveFetch:
    def _mock_urlopen(self):
        mock_response = MagicMock()
        mock_response.read.return_value = load_fixture("remotive_response.json").encode()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        return mock_response

    @patch("remotive.urllib.request.urlopen")
    def test_returns_list(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_urlopen()
        from remotive import fetch
        jobs = fetch()
        assert isinstance(jobs, list)

    @patch("remotive.urllib.request.urlopen")
    def test_jobs_have_required_fields(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_urlopen()
        from remotive import fetch
        jobs = fetch()
        required = {"title", "company", "location", "salary", "url", "source", "posted"}
        for job in jobs:
            assert required.issubset(job.keys()), f"Missing fields: {required - job.keys()}"

    @patch("remotive.urllib.request.urlopen")
    def test_source_is_remotive(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_urlopen()
        from remotive import fetch
        jobs = fetch()
        for job in jobs:
            assert job["source"] == "Remotive"

    @patch("remotive.urllib.request.urlopen")
    def test_url_is_string(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_urlopen()
        from remotive import fetch
        jobs = fetch()
        for job in jobs:
            assert isinstance(job["url"], str)
            assert job["url"].startswith("http")

    @patch("remotive.urllib.request.urlopen")
    def test_includes_description(self, mock_urlopen):
        """S8: description should be passed through for AI role detection"""
        mock_urlopen.return_value = self._mock_urlopen()
        from remotive import fetch
        jobs = fetch()
        for job in jobs:
            assert "description" in job
