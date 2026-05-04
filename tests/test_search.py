import pytest

from src.search import SearchIndex

@pytest.fixture
def search_index():
    inverted_index = {
        "life": {
            "https://example.com/page1",
            "https://example.com/page2",
        },
        "simple": {
            "https://example.com/page2",
        },
        "truth": {
            "https://example.com/page3",
        },
    }

    return SearchIndex(inverted_index)

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
    results = search_index.search_all(["life", "truth"])

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
        "https://example.com/page3",
    }
