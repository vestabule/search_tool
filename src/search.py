import json


class SearchIndex:
    def __init__(self, documents, inverted_index):
        # id -> url
        self.documents = {int(k): v for k, v in documents.items()}

        # word -> set of doc_ids
        self.inverted_index = {
            word: set(doc_ids)
            for word, doc_ids in inverted_index.items()
        }

    def search(self, word):
        doc_ids = self.inverted_index.get(word.lower(), set())
        return {self.documents[doc_id] for doc_id in doc_ids}

    def search_all(self, keywords):
        keywords = [k.lower() for k in keywords if k]
        if not keywords:
            return set()

        result = self.inverted_index.get(keywords[0], set()).copy()

        for word in keywords[1:]:
            result &= self.inverted_index.get(word, set())
            if not result:
                break

        return {self.documents[doc_id] for doc_id in result}


def load_index_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return SearchIndex(
        documents=data["documents"],
        inverted_index=data["inverted_index"],
    )
