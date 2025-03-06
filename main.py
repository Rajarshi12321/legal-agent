from legal_agent.components.full_workflow import run_user_query


if __name__ == "__main__":
    # Define the user query.
    user_query = (
        "Tell me about:  Summary Suits in Civil Proceedings under Order 37 of the CPC  "
    )
    # user_query = "How to make cake "

    result = run_user_query(user_query)
    print(result["response"])
