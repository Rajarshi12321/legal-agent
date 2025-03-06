from typing import Dict, TypedDict
from langgraph.graph import (
    StateGraph,
    END,
    START,
)  # Importing StateGraph, END, and START from langgraph.graph to define and manage state transitions within a conversational or generative AI workflow.
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from IPython.display import display, Image, Markdown
from langchain_core.runnables.graph import (
    MermaidDrawMethod,
)  # to visualize the graph of langgraph node and edges
from dotenv import load_dotenv
import os

# Load environment variables from a .env file to access sensitive information
load_dotenv()

# Set the Gemini API key for authentication with Google Generative AI services
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# user_query
# os.environ["LANGCHAIN_PROJECT"] = os.getenv(
#     "LANGCHAIN_PROJECT"
# )  # Set your custom project name

os.environ["LANGCHAIN_PROJECT"] = "LEGAL-AGENT"

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")

# Update with your API URL if using a hosted instance of Langsmith.
langchain_endpoint = os.environ["LANGCHAIN_ENDPOINT"] = (
    "https://api.smith.langchain.com"
)


# HF_TOKEN = os.environ["HF_TOKEN"] = os.getenv('HF_TOKEN')
# GEN_MODEL_ID = "deepseek-ai/deepseek-vl-1.3b-chat"

# Instantiate a chat model using Google's Gemini-1.5-flash with specified configurations
# - verbose=True enables detailed output logs for debugging
# - temperature=0.5 controls the creativity level in responses (lower values make responses more deterministic)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    verbose=True,
    temperature=0.5,
    google_api_key=GOOGLE_API_KEY,
)

from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai


from langgraph.graph import StateGraph, END, START
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from IPython.display import display, Image, Markdown
from langchain_core.runnables.graph import MermaidDrawMethod
from langchain_community.tools import DuckDuckGoSearchResults
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor


genai.configure(api_key=GOOGLE_API_KEY)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class State(TypedDict):
    query: str
    docs: str
    response: str
    is_response_sufficient: str
