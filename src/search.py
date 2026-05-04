import json


class SearchIndex:
    def __init__(self, documents, inverted_index):
        self.documents = {int(k): v for k, v in documents.items()}

        # word -> { doc_id -> frequency }
        self.inverted_index = {
            word: {int(doc): freq for doc, freq in postings.items()}
            for word, postings in inverted_index.items()
        }

    def print_raw(self, word):
        """
        Return the raw inverted index entry for a word:
        {doc_id: frequency}
        """
        postings = self.inverted_index.get(word.lower(), {})
        return dict(postings)


    def search(self, word):
        """
        Return pages ranked by frequency descending.
        """
        postings = self.inverted_index.get(word.lower(), {})
        ranked = sorted(
            postings.items(),
            key=lambda item: item[1],
            reverse=True
        )

        return [
            (self.documents[doc_id], freq)
            for doc_id, freq in ranked
        ]

    def search_all(self, keywords):
        """
        AND query: rank by summed word frequency.
        """
        keywords = [k.lower() for k in keywords if k]
        if not keywords:
            return []

        # Get common document IDs
        doc_sets = [
            set(self.inverted_index.get(word, {}).keys())
            for word in keywords
        ]

        common_docs = set.intersection(*doc_sets) if doc_sets else set()
        if not common_docs:
            return []

        # Sum frequencies across all query terms
        scores = {}

        for doc_id in common_docs:
            scores[doc_id] = sum(
                self.inverted_index[word][doc_id]
                for word in keywords
            )

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return [
            (self.documents[doc_id], score)
            for doc_id, score in ranked
        ]


def load_index_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return SearchIndex(
        documents=data["documents"],
        inverted_index=data["inverted_index"]
    )