# Importing Important libraries

import streamlit as st
from pathlib import Path

import os

import google.generativeai as genai

from langchain_community.chat_message_histories.streamlit import (
    StreamlitChatMessageHistory,
)


from datetime import datetime

from langchain.memory.buffer import ConversationBufferMemory
from langchain.schema.runnable import RunnableMap

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.callbacks.tracers.langchain import wait_for_all_tracers

import streamlit as st
from streamlit_feedback import streamlit_feedback


from langsmith import Client

from langchain_core.tracers.context import collect_runs


from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings

## Loading APIs

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

gemini_api_key = os.getenv("GOOGLE_API_KEY")


os.environ["LANGCHAIN_PROJECT"] = "GAME RECOMMENDATION"  # Set your custom project name

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")

# Update with your API URL if using a hosted instance of Langsmith.
langchain_endpoint = os.environ["LANGCHAIN_ENDPOINT"] = (
    "https://api.smith.langchain.com"
)

# Used LLM model


# Adding an event loop
import asyncio
import aiohttp


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


model = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-latest",
    api_key=gemini_api_key,
    temperature=0.3,
    convert_system_message_to_human=True,
)


# Configuring memory
memory = ConversationBufferMemory(
    chat_memory=StreamlitChatMessageHistory(key="langchain_messages"),
    return_messages=True,
    memory_key="chat_history",
)


# Load Vector DB
new_db = FAISS.load_local(
    "faiss_index", embeddings, allow_dangerous_deserialization=True
)

# Main retriever
retriever = new_db.as_retriever()

# Configuring Langsmith Client
client = Client(api_url=langchain_endpoint, api_key=langchain_api_key)


# Introducing try catch block in case you don't have a dataset with good feed back examples
try:
    # Getting best feedback examples to save in the memory context
    examples = client.list_examples(
        dataset_name="Feedbacks"
    )  # Choose your dataset_name here

    my_examples = []

    for i in examples:
        print(i.inputs)
        print(i.outputs["output"]["content"])
        print("\n\n--------\n\n")
        my_examples.append(
            (i.inputs["input"], {"output": i.outputs["output"]["content"]})
        )
except:
    my_examples = []


my_examples = my_examples[:2]

# Configuring our runnablemap
ingress = RunnableMap(
    {
        "input": lambda x: x["input"],
        "chat_history": lambda x: memory.load_memory_variables(x)["chat_history"],
        "time": lambda _: str(datetime.now()),
        "context": lambda x: retriever.get_relevant_documents(x["input"]),
        "examples": lambda x: my_examples,
    }
)

# Making the prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Only discuss games. You are a GAME RECOMMENDATION system assistant. Be humble, greet users nicely, and answer their queries."
            """
            "Instructions": 
            "Regardless of the input, always adhere to the context provided."
            "You can only make conversations based on the provided context. If a response cannot be formed strictly using the context, politely say you dont have knowledge about that topic."
            "Use the Context section to provide accurate answers, as if you knew this information innately."
            "If unsure, state that you don't know."

            "Context": {context}

            "Examples of Human feedback": 
            {examples},          
            """,
            # "system",
            # "Only and Only talk about games, nothing else, your knowledge is constraint games"
            # "You are a GAME RECOMMENDATION system assistant. You are humble AI. Greet the user nicely and answer their queries"
            # """
            #     Use the information from the Context section to provide accurate answers but act as if you knew this information innately.
            #     If unsure, simply state that you don't know.
            #     Context: {context}
            #     Here are some impressive examples of Human feedback, Do your best to try to generate these type of answer format for the specific format of questions
            #     The examples are listed below :
            #     {examples}
            #     Assistant:""",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

llm = model

# Our final chain
chain = ingress | prompt | llm


# Initialize State
if "trace_link" not in st.session_state:
    st.session_state.trace_link = None
if "run_id" not in st.session_state:
    st.session_state.run_id = None


# Sidebar to give option for Clearing message history
if st.sidebar.button("Clear message history"):
    print("Clearing message history")
    memory.clear()
    st.session_state.trace_link = None
    st.session_state.run_id = None


# When we get response from the Chatbot, then only we can see this Trace link
if st.session_state.trace_link:
    st.sidebar.markdown(
        f'<a href="{st.session_state.trace_link}" target="_blank"><button>Latest Trace: 🛠️</button></a>',
        unsafe_allow_html=True,
    )

st.header("Hey Gamers, I am a Game Recommender 🤖", divider="rainbow")

for msg in st.session_state.langchain_messages:
    avatar = "🤖" if msg.type == "ai" else None
    with st.chat_message(msg.type, avatar=avatar):
        st.markdown(msg.content)


# The main chatbot configuration to get desired out and create runs for Langsmith
if prompt := st.chat_input(placeholder="Ask me a question!"):
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        print("in chat here")

        # Getting the input
        input_dict = {"input": prompt}

        # Displaying the response from chatbot and collecting runs
        with collect_runs() as cb:
            for chunk in chain.stream(input_dict, config={"tags": ["Streamlit Chat"]}):
                full_response += chunk.content
                message_placeholder.markdown(full_response + "▌")
        memory.save_context(input_dict, {"output": full_response})

        # storing the run id in streamlit session
        ## Since the runnable sequence would come after retriever I have chosen `1` instead on `0`
        run_id = cb.traced_runs[1].id

        st.session_state.run_id = run_id

        wait_for_all_tracers()
        # Requires langsmith >= 0.0.19

        # Getting the Trace link
        url = client.share_run(run_id)

        st.session_state.trace_link = url

        message_placeholder.markdown(full_response)

# Checking if we have messages in chat
has_chat_messages = len(st.session_state.get("langchain_messages", [])) > 0


# Only show the feedback toggle if there are chat messages
if has_chat_messages:
    feedback_option = (
        "faces" if st.toggle(label="`Thumbs` ⇄ `Faces`", value=False) else "thumbs"
    )

else:
    pass

if st.session_state.get("run_id"):
    feedback = streamlit_feedback(
        feedback_type=feedback_option,  # Use the selected feedback option
        optional_text_label="[Optional] Please provide an explanation",  # Adding a label for optional text input
        key=f"feedback_{st.session_state.run_id}",
        align="flex-start",
    )

    # Define score mappings for both "thumbs" and "faces" feedback systems
    score_mappings = {
        "thumbs": {"👍": 1, "👎": 0},
        "faces": {"😀": 1, "🙂": 0.75, "😐": 0.5, "🙁": 0.25, "😞": 0},
    }

    # Get the score mapping based on the selected feedback option
    scores = score_mappings[feedback_option]

    if feedback:
        # Get the score from the selected feedback option's score mapping
        score = scores.get(feedback["score"])

        if score is not None:
            # Formulate feedback type string incorporating the feedback option and score value
            feedback_type_str = f"{feedback_option} {feedback['score']}"

            # Record the feedback with the formulated feedback type string and optional comment
            feedback_record = client.create_feedback(
                st.session_state.run_id,
                feedback_type_str,  # Updated feedback type
                score=score,
                comment=feedback.get("text"),
            )
            st.session_state.feedback = {
                "feedback_id": str(feedback_record.id),
                "score": score,
            }

            # # Incase you want to add this run with feedback to simultaneously add to a dataset
            # run_id = st.session_state.get("run_id")
            # selected_runs = client.list_runs(id=[run_id])

            # for run in tqdm(selected_runs):

            #     # print(run, "lets see")
            #     print(run.inputs)
            #     print(run.outputs)
            #     print(run.extra)
            #     print(run.feedback_stats)

            #     client.create_examples(
            #         inputs=[run.inputs],
            #         outputs=[run.outputs],
            #         feedback_stats=[run.feedback_stats],
            #         dataset_id=<your-dataset-id>,
            #     )

        else:
            st.warning("Invalid feedback score.")
