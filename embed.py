# Stage 3: embed_text - turns text into a 384-dim vector.
# Pipeline order: document.py -> chunk_text.py -> embed.py -> ingest.py -> retrieval.py

from sentence_transformers import SentenceTransformer

# Loaded once, at import time - not inside embed_text - because loading
# the model from disk is expensive. Reusing one loaded model for every
# call is far cheaper than reloading it on every single chunk.
model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_text(text):
    # Returns a 384-number vector (a numpy array) representing the
    # meaning of the text. Similar meaning -> vectors close together;
    # unrelated meaning -> vectors far apart (see similarity test below).
    return model.encode(text)


if __name__ == "__main__":
    v1 = embed_text("The cat sat on the mat")
    v2 = embed_text("A dog lay on the rug")
    v3 = embed_text("Quarterly revenue increased by 12%")

    print("cat/dog similarity:", model.similarity(v1, v2))
    print("cat/revenue similarity:", model.similarity(v1, v3))
