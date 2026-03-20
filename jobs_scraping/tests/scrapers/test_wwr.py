import os
from unittest.mock import patch, MagicMock

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures")


def load_fixture(name):
    with open(os.path.join(FIXTURE_DIR, name)) as f:
        return f.read()


class TestWwrFetch:
    def _mock_urlopen(self):
        mock_response = MagicMock()
        mock_response.read.return_value = load_fixture("wwr_response.xml").encode()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        return mock_response

    @patch("wwr.urllib.request.urlopen")
    def test_returns_list(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_urlopen()
        from wwr import fetch
        jobs = fetch()
        assert isinstance(jobs, list)

    @patch("wwr.urllib.request.urlopen")
    def test_jobs_have_required_fields(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_urlopen()
        from wwr import fetch
        jobs = fetch()
        required = {"title", "company", "location", "salary", "url", "source", "posted"}
        for job in jobs:
            assert required.issubset(job.keys()), f"Missing fields: {required - job.keys()}"

    @patch("wwr.urllib.request.urlopen")
    def test_source_is_wwr(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_urlopen()
        from wwr import fetch
        jobs = fetch()
        for job in jobs:
            assert job["source"] == "WWR"

    @patch("wwr.urllib.request.urlopen")
    def test_parses_company_from_title(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_urlopen()
        from wwr import fetch
        jobs = fetch()
        for job in jobs:
            assert job["company"] != ""
            assert ":" not in job["company"] or job["company"] != job["title"]
