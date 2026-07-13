# Stage 5: retrieve - query embedding, cosine similarity, ranked results.
# Pipeline order: document.py -> chunk_text.py -> embed.py -> ingest.py -> retrieval.py

from embed import embed_text, model
from keyword_search import keyword_score


def retrieve(query, documents, vectors):
    # Embed the query into the same 384-dim space as the stored
    # document vectors, so they can be compared directly.
    query_vector = embed_text(query)
    results = []

    # zip() walks documents and vectors together, pair by pair, since
    # they're matched by index (documents[i] goes with vectors[i]).
    for doc, vector in zip(documents, vectors):
        score = model.similarity(query_vector, vector)
        results.append((score, doc))

    # Highest similarity first, so the most relevant chunks come first.
    sorted_results = sorted(results, reverse=True)
    return sorted_results


def rrf_combine(semantic_results, keyword_results, k=60):
    # Reciprocal Rank Fusion: combine two different rankings (semantic,
    # keyword) into one score per document, using RANK POSITION rather
    # than raw scores - avoids the scale mismatch between cosine
    # similarity (-1 to 1) and keyword overlap counts (0, 1, 2...).
    # k softens how much rank 1 dominates over rank 2, rank 3, etc.
    scores = {}
    for rank, doc in enumerate(semantic_results):
        scores[doc] = scores.get(doc, 0) + 1 / (k + rank)

    # A document that ranks well in BOTH lists gets both contributions
    # added together, so it scores higher than one that only did well
    # in one method - agreement across signals is a stronger relevance
    # signal than excelling in just one.
    for rank, doc in enumerate(keyword_results):
        scores[doc] = scores.get(doc, 0) + 1 / (k + rank)

    sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_results


if __name__ == "__main__":
    from ingest import ingest

    documents, vectors = ingest(
        "The cat sat on the mat. Quarterly revenue increased by 12 percent. A dog lay on the rug.",
        "test.txt", 30, 5
    )

    results = retrieve("Tell me about pets", documents, vectors)
    for score, doc in results:
        print(score, doc.content)

    semantic_ranked = [doc for score, doc in results]
    keyword_ranked = sorted(documents, key=lambda d: keyword_score("pets", d.content), reverse=True)

    combined = rrf_combine(semantic_ranked, keyword_ranked)
    for doc, score in combined:
        print(score, doc.content)
