import streamlit as st
import requests
import json

API_URL = "http://localhost:5000"

st.set_page_config(page_title="LabDocs Q&A", layout="wide")

st.title("LabDocs Q&A")

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("Ask questions about your documents powered by RAG")

with col2:
    top_k = st.slider("Top K results", min_value=1, max_value=10, value=2)

st.divider()

question = st.text_input(
    "Enter your question:",
    placeholder="e.g., What is HLA typing used for in narcolepsy diagnosis?",
    label_visibility="collapsed"
)

if st.button("Search", type="primary"):
    if not question.strip():
        st.warning("Please enter a question")
    else:
        with st.spinner("Searching documents..."):
            try:
                response = requests.post(
                    f"{API_URL}/query",
                    json={"question": question},
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()

                    st.divider()

                    st.subheader("Answer")
                    st.write(result['answer'])

                    st.divider()
                    st.subheader(f"Sources ({len(result['sources'])} results)")

                    for i, source in enumerate(result['sources'], 1):
                        filename = source['filename']
                        score = source['score']
                        preview = source['preview']
                        segment_text = preview.rstrip('...')

                        col1, col2 = st.columns([4, 1])
                        with col1:
                            if st.button(
                                f"{i}. {filename}",
                                key=f"btn_{i}_{filename}",
                                use_container_width=True,
                                help="Click to view full document"
                            ):
                                st.session_state.selected_doc = {
                                    "filename": filename,
                                    "segment": segment_text
                                }

                        with col2:
                            st.caption(f"Score: {score:.3f}")

                        st.caption(f"**Preview:** {preview}...")
                        st.divider()

                else:
                    error_msg = response.json().get('error', 'Unknown error')
                    st.error(f"API Error: {error_msg}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API. Make sure Flask server is running on port 5000")
            except requests.exceptions.Timeout:
                st.error("Request timed out. The query took too long to process")
            except Exception as e:
                st.error(f"Error: {str(e)}")

@st.dialog("Document Viewer")
def show_document_modal():
    if "selected_doc" not in st.session_state:
        return

    doc_info = st.session_state.selected_doc
    filename = doc_info["filename"]
    segment = doc_info["segment"]

    try:
        doc_response = requests.get(
            f"{API_URL}/document/{filename}",
            params={"filename": filename, "segment": segment},
            timeout=30
        )

        if doc_response.status_code == 200:
            doc_data = doc_response.json()
            content = doc_data["content"]

            st.subheader(filename)

            if segment and segment in content:
                parts = content.split(segment)
                with st.container():
                    st.markdown(parts[0])
                    st.markdown(f":orange[**{segment}**]")
                    if len(parts) > 1:
                        st.markdown(parts[1])
            else:
                st.markdown(content)
        else:
            st.error(f"Failed to load document: {doc_response.json().get('error', 'Unknown error')}")

    except requests.exceptions.RequestException as e:
        st.error(f"Error loading document: {str(e)}")

if "selected_doc" in st.session_state:
    show_document_modal()
