---
## Live Demo
[Open the LabDocs Chat Assistant](https://2025adlmdataanalyticschallenge-hrkr9xnzmkpkl5ajeqxjjb.streamlit.app/)

# ADLM LabDocs Chat Assistant

A conversational AI assistant for laboratory procedure documents. Ask questions about lab protocols, equipment, and samples. Get answers with document citations, powered by OpenAI and semantic search.

## Features
- **Conversational chatbox** (web app) with context-aware follow-up questions
- **Cites sources** (filename and excel chunk) for every answer
- **Fast semantic search** using FAISS and Sentence Transformers
- **Easy incremental updates**: append new documents without rebuilding everything
- **Modern UI**: avatars, sidebar, clear chat, and more
- **File Upload**: upload new PDF documents directly from the sidebar
- **Downloadable Chat History**: download your entire chat session as a `.txt` file
- **Doc Dashboard**: view system stats like document count and user queries

## Adding New Documents
1. Place new PDF files in the `LabDocs/` folder.
2. Run the incremental update script:
   ```
   python add_new_documents.py
   ```
3. Restart the chat app.

OR 

- Upload new PDF documents directly from the sidebar. They are instantly added to the knowledge base and available for chat queries


## Project Structure
```
├── ask.py                # Main retrieval and QA logic
├── chat_app.py           # Streamlit chat UI
├── add_new_documents.py  # Incremental document updater
├── requirements.txt      # Python dependencies
├── lab_metadata.pkl      # Metadata for all chunks
├── lab_index.faiss       # FAISS search index
├── LabDocs/              # Folder with all lab documents
└── ...
```

## Example Usage
- "What equipment do I need for the Analytical Phase of Generating Results for 11-Deoxycortisol?"
- "And what sample?" (as a follow-up)
- "Summarize the procedure in [filename]."

---

## Running with Docker

You can run the entire app in a container using Docker:

1. **Build the Docker image:**
   ```
   docker build -t labdocs-chat .
   ```
2. **Run the container (replace YOUR_OPENAI_API_KEY):**
   ```
   docker run -p 8501:8501 -e OPENAI_API_KEY=YOUR_OPENAI_API_KEY labdocs-chat
   ```
3. **Open your browser at** [http://localhost:8501](http://localhost:8501)

---

## FAQ & Troubleshooting

**Q: How do I add new documents?**  
A: Place new PDFs in the `LabDocs/` folder and run `python add_new_documents.py` or upload new PDF documents directly from the app sidebar. They are instantly and permamnently added to the index and available for chat queries.

**Q: My app can't find the OpenAI API key!**  
A: Make sure you set `OPENAI_API_KEY` as an environment variable, in `key.env`, or as a Streamlit Cloud secret.

**Q: Can I deploy this on my own server?**  
A: Yes! Use the Dockerfile or run with `streamlit run chat_app.py` after installing dependencies.

---

