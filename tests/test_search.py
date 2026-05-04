import pytest

from src.search import SearchIndex

@pytest.fixture
def search_index():
    documents = {
        "0": "https://example.com/page1",
        "1": "https://example.com/page2",
    }

    inverted_index = {
        "life": {
            "0": 3,
            "1": 1,
        },
        "simple": {
            "1": 2,
        },
    }

    return SearchIndex(documents, inverted_index)


def test_ranked_single_word_search(search_index):
    results = search_index.search("life")

    assert results == [
        ("https://example.com/page1", 3),
        ("https://example.com/page2", 1),
    ]

def test_ranked_and_search(search_index):
    results = search_index.search_all(["life", "simple"])

    # life (1) + simple (2) = 3
    assert results == [
        ("https://example.com/page2", 3),
    ]

def test_search_missing_keyword(search_index):
    assert search_index.search("missing") == []

def test_case_insensitive_search(search_index):
    results = search_index.search("LIFE")
    assert results[0][1] == 3

def test_search_all_no_overlap(search_index):
    results = search_index.search_all(["simple", "truth"])
    assert results == []

def test_search_all_missing_keyword(search_index):
    results = search_index.search_all(["life", "missing"])
    assert results == []

def test_search_all_empty_input(search_index):
    results = search_index.search_all([])

    assert results == []

def test_search_all_single_keyword(search_index):
    results = search_index.search_all(["life"])

    assert results == [
        ("https://example.com/page1", 3),
        ("https://example.com/page2", 1),
    ]

def test_print_raw(search_index):
    postings = search_index.print_raw("life")

    assert postings == {
        0: 3,
        1: 1,
    }

def test_print_raw_case_insensitive(search_index):
    postings = search_index.print_raw("LIFE")

    assert postings == {
        0: 3,
        1: 1,
    }

def test_print_raw_missing_word(search_index):
    postings = search_index.print_raw("missing")

    assert postings == {}

def test_print_raw_returns_copy(search_index):
    postings = search_index.print_raw("life")
    postings.pop(0)

    # original index should remain unchanged
    assert search_index.print_raw("life") == {
        0: 3,
        1: 1,
    }


