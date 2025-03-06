import streamlit as st
from legal_agent.components.full_workflow import run_user_query

# Initialize session state for conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []

st.title("Legal Agent Chat App")


# Display conversation history
def display_conversation():
    for chat in st.session_state.conversation:
        if chat["role"] == "user":
            st.markdown(f"**User:** {chat['content']}")
        else:
            st.markdown(f"**Legal Agent:** {chat['content']}")


display_conversation()

# Input area for new query
user_input = st.text_input("Enter your legal query:")

if st.button("Send"):
    if user_input.strip():
        # Append user message to conversation
        st.session_state.conversation.append({"role": "user", "content": user_input})

        # Run the legal agent query workflow
        result = run_user_query(user_input)
        agent_response = result.get("response", "No response received.")

        # Append agent response to conversation
        st.session_state.conversation.append(
            {"role": "assistant", "content": agent_response}
        )

        # Clear the text input by rerunning the app
        st.experimental_rerun()
    else:
        st.error("Please enter a valid query.")
