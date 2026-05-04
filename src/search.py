import json


class SearchIndex:
    def __init__(self, inverted_index):
        self.inverted_index = {
            word: set(pages)
            for word, pages in inverted_index.items()
        }

    # Return inverted index for a specific keyword
    def search(self, word):
        return self.inverted_index.get(word.lower(), set())
    
    # Return pages matching the intersection of all passed keywords
    def search_all(self, keywords):
        """
        Return pages that contain ALL of the given keywords.

        keywords: iterable of strings
        """
        keywords = [k.lower() for k in keywords if k]

        if not keywords:
            return set()

        # Initialize with pages for the first word
        result = self.inverted_index.get(keywords[0], set()).copy()

        # Intersect with remaining words
        for word in keywords[1:]:
            result &= self.inverted_index.get(word, set())

            # Early exit if intersection is empty
            if not result:
                break

        return result


def load_index_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return SearchIndex(data)