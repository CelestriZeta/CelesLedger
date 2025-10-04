import streamlit as st
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from src.graph import app, config

# Streamed response emulator
def generate_response(user_input: str) -> str:
    messages = []
    for event in app.stream(
        {"messages": [HumanMessage(user_input)]},
        config=config,
        stream_mode="values"
    ):
        event["messages"][-1].pretty_print()
        if isinstance(event["messages"][-1], AIMessage):
            messages.append(event["messages"][-1].content)
    return messages[-1]

st.title("CelesLedger")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if user_input := st.chat_input("请输入："):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_input)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = generate_response(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.markdown(response)