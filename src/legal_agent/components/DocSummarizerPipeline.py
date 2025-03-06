from legal_agent import llm, os


class DocSummarizerPipeline:
    def __init__(
        self,
    ):
        """
        Initialize the document summarization pipeline.

        :param model: The LLM model identifier for summarization.
        :param temperature: The generation temperature.
        :param verbose: Enable verbose logging for the LLM.
        :param google_api_key: Google API key; if None, it's read from the environment.
        """

        self.llm = llm

    def summarize_docs(self, docs, query):
        """
        Summarize the retrieved documents based on the query and generate insightful bullet points.

        :param docs: List of document objects (each expected to have a 'page_content' attribute or string representation).
        :param query: The query string to focus the summary.
        :return: The generated summary with bullet points.
        """
        # Combine the content of all documents.
        combined_text = "\n\n".join(
            getattr(doc, "page_content", str(doc)) for doc in docs
        )
        prompt = (
            "You are an assistant that summarizes text. Given the following content:\n\n"
            f"{combined_text}\n\n"
            f'Summarize the content based on the query: "{query}".\n\n'
            "Instructions:\n"
            "1. Provide a brief overall summary of the content.\n"
            "2. Extract the key content required to answer the query and list it in clear bullet points.\n"
            "3. Finally, provide only the final coherent answer that integrates these bullet points, without showing any intermediate steps."
            "Finally, just answer the final coheren explaination without the 1st and 2nd step responses"
        )
        print(prompt)
        response = self.llm.invoke(prompt)
        return response.content
