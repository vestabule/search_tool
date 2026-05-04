import pytest

from src.search import SearchIndex

@pytest.fixture
def search_index():
    documents = {
        "0": "https://example.com/page1",
        "1": "https://example.com/page2",
    }

    inverted_index = {
        "life": [0, 1],
        "simple": [1],
        "truth": [0],
    }

    return SearchIndex(documents, inverted_index)

def test_single_keyword_search(search_index):
    results = search_index.search("life")

    assert results == {
        "https://example.com/page1",
        "https://example.com/page2",
    }

def test_search_is_case_insensitive(search_index):
    results = search_index.search("LIFE")

    assert results == {
        "https://example.com/page1",
        "https://example.com/page2",
    }

def test_search_all_keywords(search_index):
    results = search_index.search_all(["life", "simple"])

    assert results == {
        "https://example.com/page2",
    }

def test_search_all_no_overlap(search_index):
    results = search_index.search_all(["simple", "truth"])

    assert results == set()

def test_search_all_missing_keyword(search_index):
    results = search_index.search_all(["life", "missing"])

    assert results == set()

def test_search_all_empty_input(search_index):
    results = search_index.search_all([])

    assert results == set()

def test_search_all_single_keyword(search_index):
    results = search_index.search_all(["truth"])

    assert results == {
        "https://example.com/page1",
    }
