def normalize_url(url):
    """Normalize a URL for consistent matching across scraping, storage, and removal.

    Call this at system boundaries (CLI input, scraper output) so that
    internal code can compare URLs with simple equality checks.
    """
    return url.rstrip("/")
