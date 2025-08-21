
# Clean, working version below
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import numpy as np
import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv("key.env")

# Get API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not set in environment or .env file.")

# Load OpenAI client using the environment variable
client = OpenAI(api_key=OPENAI_API_KEY)

# Load FAISS index and metadata
index = faiss.read_index("lab_index.faiss")
index.nprobe = 10  # Increase for better recall (speed/accuracy tradeoff)
metadata = pd.read_pickle("lab_metadata.pkl")

# Load local embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

def ask_question_with_openai(question, history=None, top_k=5):
        """
        Ask a question with optional conversation history for follow-ups.
        history: list of dicts, each with 'role' ('user' or 'assistant') and 'content'.
        """
        # Support for history (for follow-up questions)
        history = history or []
        # Embed the user question
        query_vec = model.encode([question])
        # Retrieve top_k chunks from FAISS
        D, I = index.search(np.array(query_vec), top_k)
        top_chunks = metadata.iloc[I[0]]
        # Build context from retrieved chunks
        context = ""
        for _, row in top_chunks.iterrows():
            context += f"\n\n[Source: {row['filename']}, chunk {row['chunk_id']}]\n{row['text']}"
        # System prompt
        system_prompt = (
            "You are a laboratory assistant AI. Answer the user's question using ONLY the "
            "provided procedure documents. Do NOT guess or make up answers. If the answer is "
            "not in the documents, say 'I could not find that information.' Always cite the "
            "filename (and chunk ID if helpful)."
        )
        # Build message history for OpenAI
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"The following are excerpts from lab procedure documents:\n{context}"}
        ]
        # Add previous turns (excluding system)
        for turn in history:
            if turn["role"] in ("user", "assistant"):
                messages.append({"role": turn["role"], "content": turn["content"]})
        # Add the current question as the last user message
        messages.append({"role": "user", "content": question})
        # Query OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.2
        )
        # Return the response
        return response.choices[0].message.content

if __name__ == "__main__":
    question = "What sample do I need for Analytical Phase of DOCK YELLOW IgE Determination?"
    answer = ask_question_with_openai(question)
    print("\n📌 Answer:")
    print(answer)

