import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
import sys
from pathlib import Path

# Add root directory and backend directory to path
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "backend"))

from chatbot.agent import get_agent_response

# ─── STREAMLIT UI SETUP ─────────────────────────────────────────────
st.set_page_config(page_title="AI Doctor Chatbot", page_icon="🩺", layout="centered")

st.title("🩺 Digital Diagnosis AI Doctor")
st.markdown("""
Welcome to the Digital Diagnosis Assistant. Describe your symptoms naturally, and I will ask a few clarifying questions before giving a preliminary diagnosis.
""")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        AIMessage(content="Hello! I am an AI Medical Assistant. How can I help you today? Please describe any symptoms you are experiencing.")
    ]

# Display all messages in the UI
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# Handle user input from the chat bar
if prompt := st.chat_input("Type your symptoms here..."):
    # Append the user's message to the state and display it
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get the AI response
    with st.chat_message("assistant"):
        with st.spinner("The doctor is reviewing your symptoms..."):
            try:
                # Pass the entire conversation history to the agent
                response = get_agent_response(st.session_state.messages)
                st.markdown(response)
                
                # Save the AI's response to the history
                st.session_state.messages.append(AIMessage(content=response))
            except Exception as e:
                st.error(f"An error occurred: {e}")
