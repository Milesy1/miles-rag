# Stage 8: LangGraph - orchestrating steps as a graph of nodes/edges
# instead of a straight sequence of function calls. Enables branching
# decisions (e.g. "retry search if results are weak") that a fixed
# function A -> B -> C sequence can't express naturally.
from langgraph.graph import StateGraph, END
from typing import TypedDict
from ingest import ingest
from retrieval import retrieve


class GraphState(TypedDict):
    # Shape of the data passed between nodes. Each node reads from
    # this and returns an update to it.
    query: str
    documents: list
    vectors: list
    results: list
    retries: int  # caps how many times we've looped back, so a
                  # permanently-weak query can't retry forever


def say_hello(state: GraphState):
    print(f"Hello, processing query: {state['query']}")
    return {"query": state["query"]}


def retrieve_node(state: GraphState):
    text = "The cat sat on the mat. Quarterly revenue increased by 12 percent. A dog lay on the rug."
    documents, vectors = ingest(text, "test.txt", 30, 5)
    results = retrieve(state["query"], documents, vectors)
    return {"documents": documents, "vectors": vectors, "results": results}


def route_after_retrieve(state: GraphState):
    # Decision function: looks at state, returns the NAME of the next
    # node. Now also checks retries so a permanently-weak query stops
    # looping instead of running forever.
    top_score = state["results"][0][0]
    if top_score > 0.8:
        return "useful"
    if state["retries"] >= 2:
        # Give up after 2 retries - accept whatever we have.
        return "useful"
    return "not_useful"


def weak_results_node(state: GraphState):
    # Modifies the query AND increments the retry counter, then loops
    # back to retrieve_node to actually search again.
    print(f"Results were weak (retry {state['retries'] + 1}), retrying search...")
    return {
        "query": state["query"] + " additional context",
        "retries": state["retries"] + 1,
    }


graph = StateGraph(GraphState)
graph.add_node("say_hello", say_hello)
graph.add_node("retrieve_node", retrieve_node)
graph.add_node("weak_results_node", weak_results_node)
graph.set_entry_point("say_hello")
graph.add_edge("say_hello", "retrieve_node")
graph.add_conditional_edges(
    "retrieve_node",
    route_after_retrieve,
    {"useful": END, "not_useful": "weak_results_node"}
)
# The loop: weak_results_node goes back to retrieve_node instead of
# straight to END, so retrieval actually re-runs with the new query.
graph.add_edge("weak_results_node", "retrieve_node")

app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({"query": "Tell me about pets", "retries": 0})
    for score, doc in result["results"]:
        print(score, doc.content)
