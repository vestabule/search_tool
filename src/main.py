import os
import json

from crawler import QuoteCrawler
from indexer import InvertedIndex
from search import SearchIndex, load_index_from_file

indexer = InvertedIndex()
searcher = None

if __name__ == "__main__":

    # Loop shell until quits
    while True:

        i = input("\n> ").lower().strip()

        if i == "build":
            # Crawl the website
            crawler = QuoteCrawler()
            crawler.crawl(indexer)            
           
            path = indexer.build()
            print(f"Index written to {path}")

        elif i == "load":
            # Check the index has been built first
            if not os.path.exists("data/index.json"):
                print("Error: index file does not exist. Run the build command to create the index")
                continue

            searcher = load_index_from_file("data/index.json")
            print("Index data loaded from data/index.json")

        elif i[:6] == "print ":
            words = i.split(" ")[1:]
            if len(words) > 1:
                print("Error: print command requires exactly one argument")
                continue
            elif len(words) == 0:
                print("Error: print command requires an argument")

            if searcher is None:
                print("No index found, please load an index first")
                continue

            results = searcher.print_raw(words[0])
            if len(results) == 0:
                print(f"No results found for '{words[0]}'")
                continue
            for k, v in results.items():
                print(f"{k}: {v}")

        elif i[:5] == "find ":
            words = i.split(" ")[1:]
            if len(words) == 0:
                print("Error: find command requires one or more arguements")
                continue
            
            if searcher is None:
                print("No index found, please load an index first")
                continue

            results = searcher.search_all(words)
            if len(results) == 0:
                print(f"No results found")
                continue
            
            # Only care about web pages (r[0]), not the frequency (r[1])
            for r in results:
                print(r[0])

        elif i == "quit" or i == "exit":
            break
        else:
            print("Command not recognised. Valid commands are 'build', 'load', 'print', 'find' and 'quit'")