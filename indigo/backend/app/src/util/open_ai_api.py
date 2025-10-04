import os
from pathlib import Path

import numpy as np
from openai import OpenAI


class OpenAIAPI:
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        print(f"OpenAI API client initialized with key: {api_key[:8]}...")
        self.client = OpenAI(api_key=api_key)

    def embed_file(
        self,
        text: str,
        cached: Path,
        model: str = "text-embedding-3-large",
        dtype: np.dtype = np.float32,
    ) -> np.ndarray[float]:
        if cached.exists():
            arr = np.load(cached)
            return arr.astype(dtype)

        embedding = self.embed(text, model, dtype)
        np.save(cached, embedding)
        return embedding

    def embed(
        self,
        text: str,
        model: str = "text-embedding-3-large",
        dtype: np.dtype = np.float32,
    ) -> np.ndarray[float]:
        try:
            response = self.client.embeddings.create(input=text, model=model)
            return np.asarray(response.data[0].embedding, dtype=dtype)
        except Exception as e:
            print(f"Error creating embedding: {e}")
            raise
