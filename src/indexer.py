import os
import json
from collections import defaultdict

class InvertedIndex:
    def __init__(self, output_dir="data", filename="index.json"):
        self.output_dir = output_dir
        self.filename = filename
        
        self.doc_id_counter = 0
        self.url_to_doc_id = {}
        self.documents = {}

        self.inverted_index = defaultdict(lambda: defaultdict(int))

    
    def add_page(self, url, quotes):
        """
        Add a page to the index and assign it a document ID.
        """

        if url not in self.url_to_doc_id:
            doc_id = self.doc_id_counter
            self.url_to_doc_id[url] = doc_id
            self.documents[doc_id] = url
            self.doc_id_counter += 1
        else:
            doc_id = self.url_to_doc_id[url]

        for quote in quotes:
            # Quote text
            for word in self._tokenise(quote["text"]):
                self.inverted_index[word][doc_id] += 1

            # Author
            # Both split up the author
            part_author = [pa for pa in self._tokenise(quote["author"])]
            for word in part_author:
                self.inverted_index[word][doc_id] += 1
            # And add author name as single entry
            whole_name = " ".join(part_author)
            if whole_name not in part_author and not whole_name == "":
                self.inverted_index[whole_name][doc_id] += 1
            
            # Tags
            for tag in quote.get("tags", []):
                for word in self._tokenise(tag):
                    self.inverted_index[word][doc_id] += 1
            

    # Some basic tokenisation: de-capitalise, and remove common punctuation
    def _tokenise(self, text):
        for token in text.lower().split():
            yield token.strip(".,!?“”\"'()")

    # Write the index page to a file
    def build(self):
        # Build data file if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        path = os.path.join(self.output_dir, self.filename)

        data = {
            "documents": self.documents,
            "inverted_index": {
                word: dict(freqs)
                for word, freqs in self.inverted_index.items()
            },
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return path



