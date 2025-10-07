import streamlit as st
from ask import ask_question_with_openai

# --- Sidebar with logo and info ---
st.sidebar.title("LabDocs Chat Assistant")
st.sidebar.markdown("""
**Welcome!**

Ask any question about lab procedures. Answers are based only on the provided documents.
If you have a follow-up question, just ask!
""")
if st.sidebar.button("Clear Chat 🗑️"):
    st.session_state.history = []

# --- Main area ---

st.markdown(
    """
    <style>
        .block-container {padding-top: 2rem;}
        .stChatMessage {border-radius: 18px; margin-bottom: 0.5rem;}
        .stChatMessage.user {
            background-color: #e6f0fa !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🧪 LabDocs Chat Assistant 🧪")
st.divider()

# --- Chat history ---
if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    avatar = "🔍" if msg["role"] == "assistant" else "👩‍🔬"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# --- Chat input ---
user_input = st.chat_input("Type your question and press Enter...")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    # Show spinner while waiting for answer
    with st.spinner("LabDocs AI is thinking..."):
        history_for_qa = [m for m in st.session_state.history if m["role"] in ("user", "assistant")][:-1]
        answer = ask_question_with_openai(user_input, history=history_for_qa)
    st.session_state.history.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant", avatar="🧑‍🔬"):
        st.markdown(answer)
