from legal_agent import FAISS, cosine_similarity, np


class DocumentRetriever:
    def __init__(self, index_path, embeddings, top_k=7, k=25):
        """
        Initializes the retriever by loading the FAISS index and setting up embeddings.

        :param index_path: Path to the local FAISS index.
        :param embeddings: An embeddings object with an embed_documents method.
        :param k: Number of nearest neighbors to retrieve (for the FAISS retriever).
        """
        self.index_path = index_path
        self.embeddings = embeddings
        self.k = k
        self.top_k = top_k
        # Load the FAISS index as a retriever
        self.faiss_retriever = self._load_faiss_index()

    def _load_faiss_index(self):
        """
        Loads the FAISS index using the given embeddings.
        """
        retriever = FAISS.load_local(
            self.index_path, self.embeddings, allow_dangerous_deserialization=True
        ).as_retriever(search_kwargs={"k": self.k})
        return retriever

    def embed_documents(self, doc_strings):
        """
        Embeds a list of document strings and returns a numpy array of vectors.
        """
        vectors = self.embeddings.embed_documents(doc_strings)
        return np.array(vectors)

    def embed_query(self, query):
        """
        Embeds the user query and returns a 2D numpy array.
        """
        # Ensure query is embedded as a list, then get the first (and only) vector.
        query_vector = self.embeddings.embed_documents([query])[0]
        return np.array(query_vector).reshape(1, -1)

    def compute_similarity(self, query_vector, doc_vectors):
        """
        Computes cosine similarity between the query vector and document vectors.
        """
        # Returns a 1D array of similarity scores.
        return cosine_similarity(query_vector, doc_vectors)[0]

    def rerank_documents(self, user_query):
        """
        Reranks documents based on cosine similarity to the user query.

        :param doc_strings: List of document strings.
        :param user_query: The query string to compare against.
        :return: Tuple of (reranked_docs, similarity_scores, reranked_indices)
        """
        docs = self.faiss_retriever.invoke(user_query)
        # print(user_query)
        # print(doc_strings)
        # Get embeddings for documents and query
        doc_strings = [doc.page_content for doc in docs if len(doc.page_content) > 200]
        # print("Checkpoint 1: Starting reranking process.")
        doc_vectors = self.embed_documents(doc_strings)
        # print("Checkpoint 2: Documents embedded.")
        query_vector = self.embed_query(user_query)
        # print("Checkpoint 3: Query embedded.")

        # Compute similarity scores between query and all documents
        similarity_scores = self.compute_similarity(query_vector, doc_vectors)
        # print("Checkpoint 4: Similarity scores computed.")

        # Rerank document indices by descending similarity
        reranked_indices = np.argsort(similarity_scores)[::-1]
        # print("Checkpoint 5: Indices reranked.")
        reranked_docs = [doc_strings[i] for i in reranked_indices]
        # reranked_info = [doc_strings[i] for i in reranked_indices]
        reranked_docs = reranked_docs[: self.top_k]
        # print("Checkpoint 6: Top k documents selected.")
        # return reranked_docs, similarity_scores, reranked_indices
        return reranked_docs

    def pretty_print_docs(self, docs):
        """
        Pretty print the retrieved documents.

        :param docs: List of documents to print.
        """
        for i, doc in enumerate(docs, start=1):
            print(f"Document {i}:")
            print(doc)
            print("-" * 40)
