import os
import pytest
import json

from src.indexer import InvertedIndex
from src.search import load_index_from_file

# Test data
@pytest.fixture
def page_1_quotes():
    return [
        {"text": "Life is what happens when you're busy."},
        {"text": "Get busy living or get busy dying."},
    ]

@pytest.fixture
def page_2_quotes():
    return [
        {"text": "Life is really simple, but we insist on making it complicated."}
    ]


@pytest.fixture
def indexer(tmp_path):
    return InvertedIndex(output_dir=tmp_path, filename="index.json")

# Test author group quotes
def test_add_single_page(indexer, page_1_quotes):
    url = "https://example.com/page1"

    indexer.add_page(url, page_1_quotes)

    assert "life" in indexer.inverted_index
    assert indexer.inverted_index["life"] == {url}

# Test keywords in inverted index
def test_add_multiple_pages(indexer, page_1_quotes, page_2_quotes):
    url1 = "https://example.com/page1"
    url2 = "https://example.com/page2"

    indexer.add_page(url1, page_1_quotes)
    indexer.add_page(url2, page_2_quotes)

    assert indexer.inverted_index["life"] == {url1, url2}

# Test tokenisation
def test_tokenisation_normalizes_text(indexer):
    tokens = list(indexer._tokenise("Hello, WORLD!"))
    assert tokens == ["hello", "world"]

# Test the indexer writes to the correct file
def test_build_creates_index_file(indexer, page_1_quotes):
    indexer.add_page("http://test.com", page_1_quotes)
    path = indexer.build()

    assert os.path.exists(path)
    assert path.endswith("index.json")

def test_no_duplicate_urls(indexer, page_1_quotes):
    url = "https://example.com/page1"

    indexer.add_page(url, page_1_quotes)
    indexer.add_page(url, page_1_quotes)

    assert indexer.inverted_index["busy"] == {url}

def test_build_writes_index_file(indexer, page_1_quotes):
    url = "https://example.com/page1"
    indexer.add_page(url, page_1_quotes)

    path = indexer.build()

    assert os.path.exists(path)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "life" in data
    assert data["life"] == [url]

def test_load_and_search_index(indexer, page_1_quotes):
    url = "https://example.com/page1"
    indexer.add_page(url, page_1_quotes)
    path = indexer.build()

    search_index = load_index_from_file(path)

    results = search_index.search("life")
    assert results == {url}