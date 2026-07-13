# Stage 4: ingest - wires chunk_text + Document + embed_text together.
# Pipeline order: document.py -> chunk_text.py -> embed.py -> ingest.py -> retrieval.py

from chunk_text import chunk_text
from document import Document
from embed import embed_text


def ingest(text, source, chunk_size, overlap):
    # Ingestion = chunking + tagging: split raw text into overlapping
    # pieces, then wrap each piece in a Document so it carries the
    # metadata (source, page_number) needed to trace it back later.
    chunks = chunk_text(text, chunk_size, overlap)
    documents = []
    # Vectors are kept in a separate list rather than as an attribute
    # on Document, so vectors can later be swapped for a real vector
    # store (e.g. Qdrant) without changing the Document class at all.
    vectors = []
    for chunk in chunks:
        # page_number is None for now since a plain string has no
        # real pages. Real documents (e.g. PDFs) would pass the
        # actual page here instead.
        doc = Document(chunk, source, None)
        documents.append(doc)
        # Embedding happens in the same loop iteration as the Document
        # is created, so documents[i] and vectors[i] always refer to
        # the same chunk - nothing reorders either list independently.
        vectors.append(embed_text(chunk))
    return documents, vectors


if __name__ == "__main__":
    documents, vectors = ingest("abcdefghijklmnopqrstuvwxyz", "test.txt", 10, 3)
    for doc in documents:
        print(doc.content, doc.source, doc.page_number)
