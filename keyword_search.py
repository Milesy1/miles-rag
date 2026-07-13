# Stage 6: keyword_search - simple word-overlap scoring (precursor to BM25).

def keyword_score(query, content):
    # Lowercase before splitting so "Cat" and "cat" count as the same
    # word - matches how someone would expect search to behave.
    query_words = query.lower().split()
    content_words = content.lower().split()
    # set() + & finds words present in both - fast overlap check.
    overlap = set(query_words) & set(content_words)
    return len(overlap)


if __name__ == "__main__":
    score = keyword_score("dog on the rug", "A dog lay on the rug")
    print(score)
