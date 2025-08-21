
import streamlit as st
from ask import ask_question_with_openai

st.set_page_config(page_title="LabDocs Chat Assistant", page_icon="🧪")
st.title("🧪 LabDocs Chat Assistant")
st.write("Ask any question about lab procedures. Answers are based only on the provided documents.")

# Initialize chat history in session state (as a list of dicts for role/content)
if "history" not in st.session_state:
    st.session_state.history = []

# Display chat history using st.chat_message for a ChatGPT-like UI
for msg in st.session_state.history:
    with st.chat_message(msg["role"] if msg["role"] in ("user", "assistant") else "assistant"):
        st.markdown(msg["content"])

# Chat input box at the bottom
user_input = st.chat_input("Type your question and press Enter...")

if user_input:
    # Add user message to history
    st.session_state.history.append({"role": "user", "content": user_input})
    # Show the user's message immediately
    with st.chat_message("user"):
        st.markdown(user_input)
    # Call the QA function with full history (excluding system prompt)
    history_for_qa = [m for m in st.session_state.history if m["role"] in ("user", "assistant")][:-1]
    answer = ask_question_with_openai(user_input, history=history_for_qa)
    # Add assistant response to history
    st.session_state.history.append({"role": "assistant", "content": answer})
    # Show the assistant's response immediately
    with st.chat_message("assistant"):
        st.markdown(answer)
