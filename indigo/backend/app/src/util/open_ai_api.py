"""
OpenAI API client for embeddings and chat functionality.

This module provides a wrapper around the OpenAI API for generating
embeddings with caching support.
"""

import os
from pathlib import Path

import numpy as np
from openai import OpenAI
import logging


class EmbeddingsAPI:
    """OpenAI API client with embedding caching support."""
    
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        logger = logging.getLogger("app")
        logger.info(f"OpenAI API client initialized with key: {api_key[:8]}...")
        self.client = OpenAI(api_key=api_key)

    def embed_file(
        self,
        text: str,
        cached: Path,
        model: str = "text-embedding-3-large",
    ) -> np.ndarray:
        """Generate embedding with file-based caching."""
        if cached.exists():
            arr = np.load(cached)
            return arr.astype(np.float32)

        embedding = self.embed(text, model)
        np.save(cached, embedding)
        return embedding

    def embed(self, text: str, model: str = "text-embedding-3-large") -> np.ndarray:
        """Generate embedding for text using OpenAI API."""
        try:
            response = self.client.embeddings.create(input=text, model=model)
            return np.asarray(response.data[0].embedding, dtype=np.float32)
        except Exception as e:
            logger = logging.getLogger("app")
            logger.error(f"Error creating embedding: {e}")
            raise
