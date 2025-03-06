import chainlit as cl
from legal_agent.components.full_workflow import run_user_query


async def user_query_func(user_question):
    response = run_user_query(user_question)
    return response


@cl.on_chat_start
def start():
    print("Chat started!")


@cl.on_message
async def main(message: cl.Message):
    user_question = message.content
    response = await user_query_func(user_question)
    print(user_question, "see")
    await cl.Message(content=response["response"]).send()
