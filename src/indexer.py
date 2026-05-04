import os
import json
from collections import defaultdict

class InvertedIndex:
    def __init__(self, output_dir="data", filename="index.json"):
        self.output_dir = output_dir
        self.filename = filename

        self.inverted_index = defaultdict(set)

    
    def add_page(self, url, quotes):
        """
        Add all words from a single page to the index.

        url: str
        quotes: list of dicts with key "text"
        """
        for quote in quotes:
            for word in self._tokenise(quote["text"]):
                self.inverted_index[word].add(url)
            #for word in self._tokenise(quote(["author"])):
            #    self.inverted_index[word].add(url)           
                            

    # Some basic tokenisation: de-capitalise, and remove common punctuation
    def _tokenise(self, text):
        for token in text.lower().split():
            yield token.strip(".,!?“”\"'()")

    # Write the index page to a file
    def build(self):
        # Build data file if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        path = os.path.join(self.output_dir, self.filename)
        
        serialisable_index = {
            word: sorted(pages)
            for word, pages in self.inverted_index.items()
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(serialisable_index, f, indent=2, ensure_ascii=False)

        return path


