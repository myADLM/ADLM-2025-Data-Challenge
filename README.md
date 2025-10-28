---
# Live Demo
[Open the LabDocs Chat Assistant](https://2025adlmdataanalyticschallenge-hrkr9xnzmkpkl5ajeqxjjb.streamlit.app/)

# ADLM LabDocs Chat Assistant

A conversational AI assistant for laboratory procedure documents. Ask questions about lab protocols, equipment, and samples. Get answers with document citations, powered by OpenAI and semantic search.

## Features
- **Conversational chatbox** (web app) with context-aware follow-up questions
- **Cites sources** (filename and excel chunk) for every answer
- **Fast semantic search** using FAISS and Sentence Transformers
- **Modern UI**: avatars, sidebar, clear chat, and more
- **Downloadable Chat History**: download your entire chat session as a `.txt` file
- **Doc Dashboard**: view system stats like document count and user queries
- **Easy incremental updates**: add or remove documents and keep the index in sync using the incremental ingest flow
- **Admin File Upload (safe)**: upload PDF documents from the sidebar. Uploaded files are saved to `LabDocs/` and an explicit "Run incremental ingest now" action updates the vector index

## Adding New Documents

- Upload new PDF documents from the Streamlit app sidebar (admin-only). Uploaded files are saved to `LabDocs/` but are not automatically reindexed; use the in-app button "Run incremental ingest now" or run `python incremental_ingest.py` from the terminal to apply the changes to the vector index.

Notes:
- The first time you use the incremental workflow the script will perform a one-time migration that re-embeds stored chunks and assigns stable `vector_id`s. This can take time for large corpora.
- If you overwrite an existing file (same title) the ingest treats it as a replacement: old vectors for that filename are removed and the new chunks are added with new `vector_id`s.


### Project Structure
```
├── ask.py                # Main retrieval and QA logic
├── chat_app.py           # Streamlit chat UI
├── incremental_ingest.py # Incremental add/delete ingest (stable vector IDs + remove-by-filename)
├── add_new_documents.py  # Older incremental add-only updater
├── requirements.txt      # Python dependencies
├── lab_metadata.pkl      # Metadata for all chunks (now includes `vector_id` after migration)
├── lab_chunks.csv        # CSV export of metadata
├── vector_index.json     # small file storing the next available vector id
├── lab_index.faiss       # FAISS search index (IndexIDMap2 after migration)
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

**Q: How do I add, remove, or update documents?**  
A: Use the incremental ingest flow which keeps the index and metadata in sync.

Add files:
- Use the sidebar upload to save a PDF into `LabDocs/`. After upload, click the in-app "Run incremental ingest now" button to update the index.

Remove files:
- Delete the unwanted PDFs from `LabDocs/` manually. Then run:
```powershell
python incremental_ingest.py
```
The script detects filenames missing on disk, removes their associated vectors from the FAISS index, and updates `lab_metadata.pkl` / `lab_chunks.csv`.

Update files:
- Ensure the document title remains the same. Then follow the steps for "Add files". This process will detect the old duplicate and remove it along with uploading the new file. 

**Q: My app can't find the OpenAI API key.**  
A: Make sure you set `OPENAI_API_KEY` as an environment variable, in `key.env`, or as a Streamlit Cloud secret.

**Q: Can I deploy this on my own server?**  
A: Yes! Use the Dockerfile or run with `streamlit run chat_app.py` after installing dependencies.

**Q: The app is down due to inactivity**
A: No problem! Just wait for it to reload (bake in the oven).
---

