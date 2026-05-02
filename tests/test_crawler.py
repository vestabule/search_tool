import pytest
import time

from src.crawler import QuoteCrawler, SEED_URL, POLITENESS_DELAY


SAMPLE_HTML_PAGE_1 = """
<html>
<body>
    <div class="quote">
        <span class="text">“Test quote 1”</span>
        <small class="author">Author One</small>
        <a class="tag">tag1</a>
        <a class="tag">tag2</a>
    </div>
    <li class="next">
        <a href="/page/2/">Next</a>
    </li>
</body>
</html>
"""

SAMPLE_HTML_PAGE_2 = """
<html>
<body>
    <div class="quote">
        <span class="text">“Test quote 2”</span>
        <small class="author">Author Two</small>
        <a class="tag">tag3</a>
    </div>
</body>
</html>
"""


# Create a web crawler to pass as a parameter
@pytest.fixture
def crawler():
    return QuoteCrawler(SEED_URL, POLITENESS_DELAY)

# Test it stays on the right domain
def test_is_allowed(crawler):
    assert crawler.is_allowed(SEED_URL + "/page/1/")
    assert not crawler.is_allowed("https://www.bbc.co.uk/") 

# Test the parsing of quotes
def test_parse_quotes(crawler):
    quotes, soup = crawler.parse_quotes(SAMPLE_HTML_PAGE_1)

    assert len(quotes) == 1
    assert quotes[0]["text"] == "“Test quote 1”"
    assert quotes[0]["author"] == "Author One"
    assert quotes[0]["tags"] == ["tag1", "tag2"]

# Test politness delay
def test_fetch_respects_politeness_delay(crawler, monkeypatch):
    slept = []

    def fake_sleep(seconds):
        slept.append(seconds)

    def fake_get(*args, **kwargs):
        class FakeResponse:
            status_code = 200
            text = SAMPLE_HTML_PAGE_1

            def raise_for_status(self):
                pass

        return FakeResponse()

    # Modify methods to avoid real http requests
    monkeypatch.setattr(time, "sleep", fake_sleep)
    monkeypatch.setattr(crawler.session, "get", fake_get)

    crawler.fetch(SEED_URL)

    assert slept == [POLITENESS_DELAY]

# Test the crawler can follow pagination
def test_crawl_pagination(monkeypatch, crawler):
    responses = {
        SEED_URL: SAMPLE_HTML_PAGE_1,
        SEED_URL + "page/2/": SAMPLE_HTML_PAGE_2,
    }

    def fake_fetch(url):
        return responses[url]

    monkeypatch.setattr(crawler, "fetch", fake_fetch)

    crawler.crawl()

    assert len(crawler.visited) == 2

# Test it doesn't duplicate visits
def test_no_duplicate_visits(monkeypatch, crawler):
    calls = []

    def fake_fetch(url):
        calls.append(url)
        return SAMPLE_HTML_PAGE_1

    monkeypatch.setattr(crawler, "fetch", fake_fetch)

    crawler.crawl()

    # Same page should not be fetched twice
    assert len(calls) == len(set(calls))

