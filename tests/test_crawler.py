import pytest
import time
from bs4 import BeautifulSoup

from src.crawler import QuoteCrawler, SEED_URL, POLITENESS_DELAY
from src.indexer import InvertedIndex


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

@pytest.fixture
def sample_html():
    return """
    <html>
      <body>
        <a href="/page/2/">Next</a>
        <a href="/author/Albert-Einstein">Albert Einstein</a>
        <a href="/tag/life/">life</a>
        <a href="/tag/life/page/2/">life page 2</a>
        <a href="https://example.com/">External</a>
        <a href="/login">Login</a>
      </body>
    </html>
    """

# Create a web crawler to pass as a parameter
@pytest.fixture
def crawler():
    return QuoteCrawler(SEED_URL, POLITENESS_DELAY)

@pytest.fixture
def indexer():
    return InvertedIndex()

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
def test_crawl_pagination(monkeypatch, crawler, indexer):
    responses = {
        SEED_URL: SAMPLE_HTML_PAGE_1,
        SEED_URL + "page/2/": SAMPLE_HTML_PAGE_2,
    }

    def fake_fetch(url):
        return responses[url]

    monkeypatch.setattr(crawler, "fetch", fake_fetch)

    crawler.crawl(indexer)

    assert len(crawler.visited) == 2

# Test it doesn't duplicate visits
def test_no_duplicate_visits(monkeypatch, crawler, indexer):
    calls = []

    def fake_fetch(url):
        calls.append(url)
        return SAMPLE_HTML_PAGE_1

    monkeypatch.setattr(crawler, "fetch", fake_fetch)

    crawler.crawl(indexer)

    # Same page should not be fetched twice
    assert len(calls) == len(set(calls))

def test_extracts_relevant_internal_links(crawler, sample_html):
    soup = BeautifulSoup(sample_html, "html.parser")
    base_url = "https://quotes.toscrape.com/"

    links = crawler.extract_links(soup, base_url)

    assert "https://quotes.toscrape.com/page/2/" in links
    assert "https://quotes.toscrape.com/author/Albert-Einstein" in links
    assert "https://quotes.toscrape.com/tag/life/" in links
    assert "https://quotes.toscrape.com/tag/life/page/2/" in links

def test_ignores_external_links(crawler, sample_html):
    soup = BeautifulSoup(sample_html, "html.parser")
    base_url = "https://quotes.toscrape.com/"

    links = crawler.extract_links(soup, base_url)

    assert all("example.com" not in link for link in links)

def test_relative_urls_resolved(crawler):
    html = """
    <html>
      <body>
        <a href="/author/Mark-Twain">Mark Twain</a>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    base_url = "https://quotes.toscrape.com/page/1/"

    links = crawler.extract_links(soup, base_url)

    assert links == {
        "https://quotes.toscrape.com/author/Mark-Twain"
    }

