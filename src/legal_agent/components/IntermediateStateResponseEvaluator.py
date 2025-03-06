from legal_agent import llm


class IntermediateStateResponseEvaluator:
    def __init__(self, llm=llm, response_length_threshold: int = 50):
        """
        Initialize the response evaluator with an LLM.

        Args:
            llm: An instance of an LLM that supports asynchronous invocation (e.g., ChatOpenAI).
            response_length_threshold: Minimum number of characters required in the response.
        """
        self.llm = llm
        self.response_length_threshold = response_length_threshold

    def is_response_sufficient(self, query: str, response: str) -> str:
        """
        Use the LLM to judge whether a previously generated response is sufficiently
        complete and correct for the given query.

        Args:
            query: The original user query.
            response: The LLM-generated response that needs evaluation.

        Returns:
            "yes" if the LLM judges the response as sufficient, "no" otherwise.
        """
        # Quick check on response length
        if not response or len(response.strip()) < self.response_length_threshold:
            return "no"

        # Construct the evaluation prompt
        prompt = (
            "You are an expert evaluator. Given the following question and the generated answer, "
            "determine if the answer sufficiently and correctly addresses the question in simple way. "
            "Answer with only 'yes' or 'no'.\n\n"
            f"Question: {query}\n\n"
            f"Generated Answer: {response}\n\n"
            "Is the answer sufficiently complete and correct?"
        )

        # Invoke the LLM asynchronously
        evaluation = self.llm.invoke([{"role": "user", "content": prompt}])
        # print(evaluation)
        judgment = evaluation.content.strip().lower()

        # Expect the LLM to return either a clear "yes" or "no"
        return "yes" if "yes" in judgment else "no"
