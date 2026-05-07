# Quotes Search Engine (Educational Web Crawler & Indexer)

## Project Purpose

This project is an **educational web crawling, indexing, and search system** built around  
https://quotes.toscrape.com, a site specifically designed for scraping practice.

The system demonstrates the **core components of a search engine pipeline**:

1. **Polite web crawling**
2. **Link discovery** (pagination, authors, tags)
3. **Text extraction** (quotes, authors, tags)
4. **Inverted index construction**
   - Pointer-based (document IDs)
   - Frequency-aware (term counts per page)
5. **Ranked search**
   - Single-term search
   - Multi-term AND queries
6. **Command-line query parsing**
7. **Comprehensive automated testing with pytest**

---

## Project Structure

```text
└── project/
    ├── src/
    │   ├── crawler.py
    │   ├── indexer.py
    │   ├── main.py
    │   └── search.py
    ├── tests/
    │   ├── test_crawler.py
    │   ├── test_indexer.py
    │   └── test_search.py
    ├── data/
    │   └── index.json
    ├── README.md
    └── requirements.txt
```

## Installation Instructions

### 1. Clone the repository
    git clone git@github.com:vestabule/search_tool.git
    cd search_tool.git

### 2. Create a virtul environment
    python -m venv venv
    source venv/bin/activate # macOS/Linux
    venv/Scripts/activate # Windows

### 3. Install dependencies
    pip install -r requirements.txt

## Dependencies

The project depends on:<br>
<ul>
<li>requests - for HTTP web crawling</li>
<li>beautifulsoup4 - HTML parsing and link extraction</li>
<li>pytest - automated testing</li>
</ul>


## Usage Examples

### build
    > build
    Fetching: <page>
    ...
    Index written to data/index.json

The build commands crawls the website, builds and index and saves it to a file.
It will overwrite any existing index there.
### load
    > load
    Index data loaded from data/index.json

The load commands loads the data from the index file ready to search. 
An index file must have been created first
### print <arg>
    > print until
    Inverted index for 'until'
    0: 1
    36: 1
    54: 1
    203: 2
    213: 2

The print command takes one argument and returns the raw inverted index entry matching that argument. An index must have been loaded with the load command first. 

### find <args>
    > find today and
    https://quotes.toscrape.com/tag/life/
    https://quotes.toscrape.com/tag/life/page/1/
    https://quotes.toscrape.com/page/3/  

The find command takes one or more arguments and return all pages containing every supplied argument. 

