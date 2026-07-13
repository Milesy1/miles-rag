# Stage 1: Document class - the data container each chunk gets wrapped in.
# Pipeline order: document.py -> chunk_text.py -> embed.py -> ingest.py -> retrieval.py

class Document:
    # A Document wraps one chunk of text with the metadata needed to
    # trace it back to where it came from — required later for
    # citations and reranking. __init__ doesn't create the object;
    # it configures one that already exists.
    def __init__(self, content, source, page_number):
        self.content = content
        self.source = source
        self.page_number = page_number


if __name__ == "__main__":
    d = Document("hello", "test.txt", 3)
    print(d.content)
    print(d.source)
    print(d.page_number)
