# from QA_app.components.data_querying import user_query
from chainlit import on_chat_start, on_message, LangchainCallbackHandler
import chainlit as cl
from main_app_deploy.components.data_querying import my_query


import os

os.environ["LITERAL_API_KEY"] = os.getenv("LITERAL_API_KEY")

os.environ["LANGCHAIN_PROJECT"] = "GAME RECOMMENDATION"

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")


# user_query


async def user_query_func(user_question):
    response = my_query(user_question)
    # Replace this with your actual logic for processing the user query
    # It could involve interacting with an LLM, searching web documents, etc.
    # For illustration purposes, let's just return a simple response
    return response


@cl.on_chat_start
def start():
    # user_query

    print("Chat started!")


@cl.on_message
async def main(message: cl.Message):
    # user_query
    user_question = message.content
    # response = user_query(user_question)
    # response = await user_query_func("What happended to the birds")
    response = await user_query_func(user_question)
    print(user_question, "see")
    # user_query = cl.make_async(user_query)

    # await user_query("What happended to the birds")
    # print(user_question, "see22222222")

    # Use LangchainCallbackHandler to capture the final answer
    # callback_handler = LangchainCallbackHandler(stream_final_answer=True)
    # response = await cl.make_async(user_query)(user_question)
    # response = await cl.make_async(user_query)(user_question)

    # await message.reply(response)
    await cl.Message(content=response).send()


# # Run the Chainlit app
# cl.run()
