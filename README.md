                                                                                           
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

## Adding New Documents
1. Place new PDF files in the `LabDocs/` folder.
2. Run the incremental update script:
   ```
   python add_new_documents.py
   ```
3. Restart the chat app.


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

