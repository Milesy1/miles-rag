# Miles' RAG

A RAG (Retrieval-Augmented Generation) system built from first principles, one piece at a time — no scaffolding, no generated boilerplate. The goal is implementation fluency, not just conceptual familiarity: progress here is measured in code run, not concepts confirmed.

## Built so far

- **`document.py`** — `Document` class. Wraps one chunk of text with the metadata (source, page_number) needed to trace an answer back to where it came from.
- **`chunk_text.py`** — `chunk_text(text, chunk_size, overlap)`. Splits raw text into overlapping pieces so sentences sitting on a chunk boundary don't lose meaning.
- **`embed.py`** — `embed_text(text)`. Turns text into a 384-dimensional vector using a local `sentence-transformers` model (`all-MiniLM-L6-v2`). Verified: semantically similar sentences produce close vectors (cosine similarity), unrelated sentences don't.
- **`ingest.py`** — `ingest(text, source, chunk_size, overlap)`. Wires chunking + tagging + embedding together: raw text in, `(documents, vectors)` out.
- **`retrieval.py`** — `retrieve(query, documents, vectors)`: embeds a query and ranks stored documents by cosine similarity. `rrf_combine(semantic_results, keyword_results, k=60)`: fuses semantic ranking with keyword ranking via Reciprocal Rank Fusion — combines by rank position (not raw score) to avoid the scale mismatch between cosine similarity and overlap counts. A document ranking well in both methods outranks one strong in only one.
- **`keyword_search.py`** — `keyword_score(query, content)`. Lexical relevance via lowercased token-set overlap — a simplified stand-in for BM25, used as the keyword half of hybrid retrieval.
- **`async_demo.py`** — async fundamentals side-quest. `run_sequential()` vs `run_concurrent()` (via `asyncio.gather`) prove sequential waits stack up (6.00s for 3+2+1s) while concurrent waits overlap (3.01s) — direct evidence `await` only pauses one task, not the whole program.
- **`graph.py`** — LangGraph workflow with a real retry loop. `say_hello` -> `retrieve_node` (runs real `ingest`/`retrieve`) -> conditional edge (`route_after_retrieve`) branches to `weak_results_node` if the top score is low. `weak_results_node` modifies the query and loops back to `retrieve_node`, capped at 2 retries to avoid infinite looping. Proves state-based decision routing plus a genuine retry mechanism, not just a fixed function sequence.
- **`eval.py`** — basic eval harness. A set of `(query, expected_keyword)` test cases, run through real `retrieve()`, scored pass/fail on whether the expected keyword appears in the top result. Same core idea behind production eval systems, simplified.

## Pipeline so far

```
raw text -> chunk_text() -> [chunks] -> ingest() -> [Document, ...] + [vector, ...]
                                                          ^
                                                   embed_text() per chunk

query -> retrieve() (semantic, cosine similarity)  --\
       -> keyword_score() (lexical overlap)          }-> rrf_combine() -> ranked [Document, ...]
                                                      --/

LangGraph: say_hello -> retrieve_node -> [route_after_retrieve] -> useful? -> END
                                            ^                   -> not_useful? -> weak_results_node -\
                                            |______________________________________________________/
                                            (loops back, capped at 2 retries)

eval.py: [(query, expected_keyword), ...] -> retrieve() -> pass/fail per case
```

## Remaining curriculum

- Pydantic v2 fluency — via LangGraph nodes (state validation beyond plain TypedDict)
- PyTorch basics — tensors, basic ops, a training loop (fast.ai: https://course.fast.ai/)
- Implement a paper — Corrective RAG (CRAG) planned next, applied to a real TouchDesigner documentation RAG bot (separate project, reusing existing documentation content)
- CS224N — Stanford NLP course (free self-study: https://web.stanford.edu/class/cs224n/), layered in alongside the above
