import os
import pytest
import json

from src.indexer import InvertedIndex

# Test data
@pytest.fixture
def page_1_quotes():
    return [
        {
            "text": "Life is life is beautiful",
            "author": "Confucius",
            "tags": ["life", "simplicity"],
        },
        {
            "text": "Life happens while you are busy",
            "author": "John Lennon",
            "tags": ["life", "busy"]
        }
    ]

@pytest.fixture
def page_2_quotes():
    return [
        {
            "text": "Life is really simple",
            "author": "Confucius",
        }
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

def test_word_frequency_count(indexer, page_1_quotes):
    url = "https://example.com/page1"
    indexer.add_page(url, page_1_quotes)

    # "life" appears 3 times
    assert indexer.inverted_index["life"][0] == 5

def test_frequency_across_pages(indexer, page_1_quotes, page_2_quotes):
    url1 = "https://example.com/page1"
    url2 = "https://example.com/page2"

    indexer.add_page(url1, page_1_quotes)  # life x3
    indexer.add_page(url2, page_2_quotes)  # life x1

    assert indexer.inverted_index["life"] == {
        0: 5,
        1: 1,
    }

def test_build_stores_frequencies(indexer, page_1_quotes):
    url = "https://example.com/page1"
    indexer.add_page(url, page_1_quotes)

    path = indexer.build()
    assert os.path.exists(path)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["documents"]["0"] == url
    assert data["inverted_index"]["life"]["0"] == 5

def test_author_words_indexed(indexer, page_1_quotes):
    url = "https://example.com/page1"
    indexer.add_page(url, page_1_quotes)

    assert indexer.inverted_index["confucius"][0] == 1
    assert indexer.inverted_index["john"][0] == 1
    assert indexer.inverted_index["lennon"][0] == 1

def test_author_and_text_both_contribute(indexer):
    quotes = [
        {"text": "Life is life", "author": "Life Expert"},
    ]
    url = "https://example.com/page1"

    indexer.add_page(url, quotes)

    # "life" appears twice in text + once in author name
    assert indexer.inverted_index["life"][0] == 3

def test_json_contains_author_terms(indexer, page_1_quotes):
    url = "https://example.com/page1"
    indexer.add_page(url, page_1_quotes)

    path = indexer.build()
    assert os.path.exists(path)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "confucius" in data["inverted_index"]
    assert data["inverted_index"]["confucius"]["0"] == 1

def test_whole_author_name_indexed(indexer, page_1_quotes):
    url = "https://example.com/page1"
    indexer.add_page(url, page_1_quotes)

    assert indexer.inverted_index["john"][0] == 1
    for p in indexer.inverted_index:
        print(p)
    assert indexer.inverted_index["john lennon"][0] == 1

def test_tag_words_indexed(indexer, page_1_quotes):
    url = "https://example.com/page1"
    indexer.add_page(url, page_1_quotes)

    assert indexer.inverted_index["life"][0] >= 2
    assert indexer.inverted_index["simplicity"][0] == 1
    assert indexer.inverted_index["busy"][0] == 2

def test_tags_contribute_to_frequency(indexer):
    quotes = [
        {
            "text": "Simple life",
            "author": "Life Expert",
            "tags": ["life", "life"],
        }
    ]
    url = "https://example.com/page1"
    indexer.add_page(url, quotes)

    # "life": text (1) + author (1) + tags (2) = 4
    assert indexer.inverted_index["life"][0] == 4

def test_tag_frequency_multiple_quotes(indexer):
    quotes = [
        {"text": "A", "author": "A", "tags": ["wisdom"]},
        {"text": "B", "author": "B", "tags": ["wisdom"]},
    ]
    url = "https://example.com/page1"
    indexer.add_page(url, quotes)

    assert indexer.inverted_index["wisdom"][0] == 2

def test_json_contains_tag_terms(indexer, page_1_quotes):
    url = "https://example.com/page1"
    indexer.add_page(url, page_1_quotes)

    path = indexer.build()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "simplicity" in data["inverted_index"]
    assert data["inverted_index"]["simplicity"]["0"] == 1


