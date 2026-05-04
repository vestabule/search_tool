import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


SEED_URL = "https://quotes.toscrape.com/"
POLITENESS_DELAY = 6  # seconds


class QuoteCrawler:
    def __init__(self, seed_url=SEED_URL, politeness_delay=6):
        self.seed_url = seed_url
        self.politeness_delay = politeness_delay
        self.visited = set()
        self.session = requests.Session()

        parsed_seed = urlparse(seed_url)
        self.allowed_domain = parsed_seed.netloc

        self.session.headers.update({
            "User-Agent": "EducationalCrawler/1.0 (polite scraping demo)"
        })

        self.quotes = []

    def is_allowed(self, url):
        """Ensure we stay within the seed domain."""
        return urlparse(url).netloc == self.allowed_domain

    def fetch(self, url):
        """Fetch a page with politeness delay."""
        print(f"Fetching: {url}")
        time.sleep(self.politeness_delay)
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        return response.text

    def parse_quotes(self, html):
        """Extract quotes from the page."""
        soup = BeautifulSoup(html, "html.parser")
        quotes = []

        for quote_div in soup.select("div.quote"):
            text = quote_div.select_one("span.text").get_text(strip=True)
            author = quote_div.select_one("small.author").get_text(strip=True)
            tags = [tag.get_text(strip=True) for tag in quote_div.select("a.tag")]

            quotes.append({
                "text": text,
                "author": author,
                "tags": tags
            })

        return quotes, soup

    def extract_links(self, soup, base_url):
        """
        Extract all relevant internal links from a page.
        """
        discovered = set()

        for a in soup.select("a[href]"):
            href = a["href"]
            url = urljoin(base_url, href)
            parsed = urlparse(url)

            if not self.is_allowed(url):
                continue

            if url not in self.visited:
                discovered.add(url)

        return discovered


    def crawl(self, indexer):
        """Main crawl loop (pagination-based)."""
        queue = [self.seed_url]

        while queue:
            url = queue.pop(0)

            if url in self.visited:
                continue

            self.visited.add(url)

            try:
                html = self.fetch(url)
            except requests.RequestException as e:
                print(f"Failed to fetch {url}: {e}")
                continue

            quotes, soup = self.parse_quotes(html)

            # Index information
            indexer.add_page(url, quotes)

            # Find page links
        
            new_links = self.extract_links(soup, url)

            for link in sorted(new_links):
                if link not in self.visited:
                    queue.append(link)

            # next_link = soup.select_one("li.next > a")
            # if next_link:
            #     next_url = urljoin(url, next_link["href"])
            #     if next_url not in self.visited:
            #         queue.append(next_url)
                


if __name__ == "__main__":
    crawler = QuoteCrawler(SEED_URL, POLITENESS_DELAY)
    crawler.crawl()