from legal_agent import State, llm, embeddings, END, START, StateGraph, faiss_index_path


from typing import Dict, TypedDict


from legal_agent.components.DocumentRetriever import DocumentRetriever
from legal_agent.components.DocSummarizerPipeline import DocSummarizerPipeline
from legal_agent.components.IntermediateStateResponseEvaluator import (
    IntermediateStateResponseEvaluator,
)
from legal_agent.components.WebSearchAgent import WebSearchAgent


def faiss_content_retriever(state: State) -> State:
    print("\nEntering faiss_content_retriever")
    # Initialize the retriever with the FAISS index location
    doc_retriever = DocumentRetriever(faiss_index_path, embeddings)

    # Rerank documents based on cosine similarity
    re_ranked_docs = doc_retriever.rerank_documents(state["query"])

    # print(f"\nRetrieved documents: {re_ranked_docs}")

    return {"docs": re_ranked_docs}


def grounded_response(state: State) -> State:
    print("\nEntering grounded_response")
    # Create the summarization pipeline with the retriever.
    doc_summarize = DocSummarizerPipeline()

    # Process the query: retrieve documents and generate the summary.
    result = doc_summarize.summarize_docs(state["docs"], state["query"])
    print(f"\nGenerated response: {result}")

    return {"response": result}


def response_judge(state: State) -> State:
    print("\nEntering response_judge")
    evaluator = IntermediateStateResponseEvaluator()
    query = state["query"]
    generated_response = state["response"]

    result = evaluator.is_response_sufficient(query, generated_response)
    print(f"\nResponse sufficient: {result}")

    return {"is_response_sufficient": result}


def web_response(state: State) -> State:
    print(f"""\n\nweb_response state check\n-{state["is_response_sufficient"]}\n-""")
    print("\n\nRetrived Docs weren't suitable to answer, so going for web search")
    print("\nEntering web_response")
    agent = WebSearchAgent()
    user_query = state["query"]
    output = agent.web_based_response(user_query)
    # print(f"\nWeb search response: {output}")

    return {"response": output}


def route_from_response_judge(state):
    if state.get("is_response_sufficient") == "yes":
        print("returning -yes")

        return "yes"  # Correct the return value here as well
    print("returning -no")
    return "no"


# Create the workflow graph
workflow = StateGraph(State)

# Add nodes for each state in the workflow
workflow.add_node(
    "faiss_content_retriever", faiss_content_retriever
)  # Initial categorization node
workflow.add_node("grounded_response", grounded_response)  # Initial categorization node
workflow.add_node("response_judge", response_judge)  # Initial categorization node
workflow.add_node("web_response", web_response)  # Initial categorization node


workflow.add_edge(START, "faiss_content_retriever")

# Define the workflow edges
workflow.add_edge("faiss_content_retriever", "grounded_response")
workflow.add_edge("grounded_response", "response_judge")

# Set up the conditional edge from "response_judge"
# Mapping: if "yes" then route to END, if "no" then route to "web_response"
workflow.add_conditional_edges(
    "response_judge", route_from_response_judge, {"yes": END, "no": "web_response"}
)


# Ensure that if the workflow goes to web_response, it then routes to END.
workflow.add_edge("web_response", END)
# workflow.add_edge("web_response", END)

workflow.add_edge("response_judge", END)

# Set the initial entry point to start the workflow at the categorize node
workflow.set_entry_point("faiss_content_retriever")

# Compile the workflow graph into an application
app = workflow.compile()


def run_user_query(query: str) -> Dict[str, str]:
    """Process a user query through the LangGraph workflow.

    Args:
        query (str): The user's query

    Returns:
        Dict[str, str]: A dictionary containing the query's category and response
    """
    results = app.invoke({"query": query})
    return {
        # "category": results["category"],
        "response": results["response"]
    }
