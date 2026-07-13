# Stage 9: basic evals - measure whether retrieval actually works,
# using known (query, expected_keyword) pairs instead of eyeballing output.
from ingest import ingest
from retrieval import retrieve

test_cases = [("Tell me about pets", "dog"), ("What happened to revenue", "revenue")]


def run_eval(test_cases, documents, vectors):
    # Runs each test query through real retrieve(), checks whether the
    # expected keyword shows up in the top result - a simple pass/fail
    # signal instead of eyeballing whether output "looks right".
    passed = 0
    for query, expected in test_cases:
        results = retrieve(query, documents, vectors)
        top_doc = results[0][1]
        if expected in top_doc.content:
            passed += 1
            print(f"PASS: '{query}'")
        else:
            print(f"FAIL: '{query}' - expected '{expected}' not in top result")
    print(f"\n{passed}/{len(test_cases)} passed")


if __name__ == "__main__":
    text = "The cat sat on the mat. Quarterly revenue increased by 12 percent. A dog lay on the rug."
    documents, vectors = ingest(text, "test.txt", 30, 5)
    run_eval(test_cases, documents, vectors)
