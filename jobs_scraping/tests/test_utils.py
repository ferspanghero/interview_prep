from utils import normalize_url


class TestNormalizeUrl:
    def test_strips_trailing_slash(self):
        assert normalize_url("https://example.com/jobs/1/") == "https://example.com/jobs/1"

    def test_no_trailing_slash_unchanged(self):
        assert normalize_url("https://example.com/jobs/1") == "https://example.com/jobs/1"

    def test_multiple_trailing_slashes(self):
        assert normalize_url("https://example.com/jobs/1///") == "https://example.com/jobs/1"

    def test_root_url_slash_stripped(self):
        assert normalize_url("https://example.com/") == "https://example.com"
