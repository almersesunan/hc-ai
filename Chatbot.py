import os
import streamlit as st
from langchain_core.messages import HumanMessage
from agentic_ai.ai_agent import graph, load_checkpoint, save_checkpoint

# API URLs
API_BASE_URL = "http://localhost:8000"
API_URL_CANDIDATE = f"{API_BASE_URL}/candidate_analysis/"

st.set_page_config(
    page_title="AI-Powered Human Capital System",
    page_icon="🧑",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.markdown("---")
    st.caption("AI-Powered Human Capital System")
    st.caption("© 2025 HCIS - Sinar Mas Land")

st.title('AI-Powered Human Capital System')
st.markdown("""
    **An AI-Powered Human Capital System represents the next generation of HR technology, \
    moving beyond traditional administrative functions to a strategic, data-driven platform. \
    By leveraging artificial intelligence and machine learning, this system provides unprecedented \
    insights into workforce dynamics, automates complex processes, and empowers leaders to make fairer, \
    faster, and more effective decisions.**
""")

# Streamlit chat interface
if "thread_id" not in st.session_state:
    st.session_state.thread_id = os.urandom(4).hex()
if "state" not in st.session_state:
    st.session_state.state = load_checkpoint(st.session_state.thread_id)
if "messages" not in st.session_state.state:
    st.session_state.state["messages"] = []

st.markdown("### 🤖 Chat with DIBA")

for msg in st.session_state.state["messages"]:
    if hasattr(msg, "content"):
        st.chat_message("user" if isinstance(msg, HumanMessage) else "assistant").write(msg.content)

user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.state["messages"].append(HumanMessage(content=user_input))
    try:
        st.session_state.state = graph.invoke(st.session_state.state)
        ai_msg = st.session_state.state["messages"][-1].content
        st.chat_message("assistant").write(ai_msg)
        save_checkpoint(st.session_state.thread_id, st.session_state.state)
        st.rerun()
    except Exception as e:
        st.error(f"⚠️ Error during graph invocation: {e}")

# --- Export Chat Button ---
if st.session_state.state["messages"]:
    # Prepare chat history as plain text
    chat_lines = []
    for msg in st.session_state.state["messages"]:
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        chat_lines.append(f"{role}: {msg.content}")
    chat_text = "\n".join(chat_lines)

    col1, col2, col3 = st.columns([5, 1, 2])
    with col3:
        st.download_button(
            label="Download Chat History",
            data=chat_text,
            file_name="chat_history.txt",
            mime="text/plain"
        )