import os
import pytest
import json

from src.indexer import InvertedIndex

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


def test_document_id_assignment(indexer, page_1_quotes, page_2_quotes):
    url1 = "https://example.com/page1"
    url2 = "https://example.com/page2"

    indexer.add_page(url1, page_1_quotes)
    indexer.add_page(url2, page_2_quotes)

    assert indexer.documents == {
        0: url1,
        1: url2,
    }

# Test keywords in inverted index
def test_add_multiple_pages(indexer, page_1_quotes, page_2_quotes):
    url1 = "https://example.com/page1"
    url2 = "https://example.com/page2"

    indexer.add_page(url1, page_1_quotes)
    indexer.add_page(url2, page_2_quotes)

    assert len(indexer.inverted_index["life"]) == 2
    assert indexer.documents == {0: url1, 1: url2}

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

def test_no_duplicate_document_ids(indexer, page_1_quotes):
    url = "https://example.com/page1"

    indexer.add_page(url, page_1_quotes)
    indexer.add_page(url, page_1_quotes)

    assert len(indexer.documents) == 1
    assert indexer.url_to_doc_id[url] == 0

def test_inverted_index_uses_doc_ids(indexer, page_1_quotes):
    url = "https://example.com/page1"
    indexer.add_page(url, page_1_quotes)

    life_docs = indexer.inverted_index["life"]
    assert life_docs == {0}

def test_keyword_maps_to_multiple_documents(indexer, page_1_quotes, page_2_quotes):
    url1 = "https://example.com/page1"
    url2 = "https://example.com/page2"

    indexer.add_page(url1, page_1_quotes)
    indexer.add_page(url2, page_2_quotes)

    assert indexer.inverted_index["life"] == {0, 1}

def test_build_writes_pointer_based_index(indexer, page_1_quotes):
    url = "https://example.com/page1"
    indexer.add_page(url, page_1_quotes)

    path = indexer.build()
    assert os.path.exists(path)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["documents"]["0"] == url
    assert data["inverted_index"]["life"] == [0]
