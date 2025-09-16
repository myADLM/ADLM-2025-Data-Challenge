import hashlib
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Protocol, Dict, Type
import requests

import faiss
import numpy as np
import polars as pl
import OpenAI


class VectorSearch:
    """
    A class to represent a vector search for document retrieval using embeddings.

    This class utilizes an embedding model to convert text documents into embeddings,
    stores them in a FAISS index for efficient similarity search, and supports caching
    of embeddings for faster repeated queries.

    Attributes:
        embedding_model (EmbeddingModel): The embedding model used for text-to-vector conversion.
        cache_dir (Path): Cache directory responsible for reading and saving embeddings
        data (pl.DataFrame): A DataFrame containing the documents and their corresponding embeddings.
        index (faiss.IndexFlatL2): A FAISS index for similarity search.
    """

    def __init__(self, documents: list[str], embedder: str, embedding_cache: Path | str):
        """
        Initializes the VectorDatabase with a set of documents.

        Args:
            documents: A list of text documents to embed and search.
            embedder: Name of the embedding model to use.
            embedding_cache: Cache directory responsible for reading and saving embeddings
        """
        self.embedding_model = get_embedding_model(embedder)
        self.cache_dir = Path(embedding_cache) / embedder
        self.cache_dir.mkdir(parents=True, exist_ok=True)
            
        self.data = pl.DataFrame({
            "document": documents,
            "embedding": self._generate_embeddings(documents)
        }).dropna(subset=['embedding'])
        embeddings = np.vstack(self.data["embedding"])
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

    def search(self, text: str, n: int) -> tuple[pl.DataFrame, np.ndarray]:
        """
        Searches the vector database for the top-N most similar documents to the input text.

        Args:
            text: The query text to search for.
            n: The number of top similar documents to return.

        Returns:
            A tuple containing (DataFrame with top-N similar documents, similarity scores).
        """
        embedded_query = self._get_embedding(text)
        d, i = self.index.search(np.array([embedded_query]), n)
        return self.data.iloc[[i[0][j] for j in range(n)]], d[0]

    def _generate_embeddings(self, documents: list[str]) -> list[np.ndarray]:
        """
        Generates embeddings for a list of documents using parallel processing.
        
        Args:
            documents: List of text documents to embed
            
        Returns:
            List of embedding vectors corresponding to the input documents
        """
        if len(documents) == 0:
            return []

        cpu_count = os.cpu_count() or 1
        # Use min of CPU count and 8 to avoid overwhelming the system
        max_workers = min(cpu_count, 8)
        
        # For small datasets, use sequential processing to avoid overhead
        # Also use sequential if max_workers is 1
        if len(documents) < 10 or max_workers == 1:
            return [self._get_embedding(doc) for doc in documents]
        
        embeddings = [None] * len(documents)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(self._get_embedding, doc): i 
                for i, doc in enumerate(documents)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    embeddings[index] = future.result()
                except Exception as e:
                    raise Exception(f"Error generating embedding for document {index}: {e}")
        
        return embeddings

    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Generates or retrieves the embedding for a given text.

        Args:
            text: The text to embed.

        Returns:
            The embedding vector for the input text.
        """
        text_sha = hashlib.sha1(text.encode()).hexdigest()
        cache_file = self.cache_dir / f"{text_sha}.npy"

        if cache_file.exists():
            return np.load(cache_file)
        result = self.embedding_model.embed(text)
        np.save(cache_file, result)
        return result


# ================================
# Embedding Models
# ================================

class EmbeddingModel(Protocol):
    """Protocol for embedding models."""

    def embed(self, text: str) -> np.ndarray:
        """Embed the text as a vector."""
        ...

class _EmbeddingModelRegistry:
    """Registry for embedding models based on names."""

    _models: Dict[str, Type[EmbeddingModel]] = {}

    @classmethod
    def register(cls, name: str):
        """
        Decorator to register an embedding model class for a given name.
        Only one model per name is allowed.

        Args:
            name: Name of the embedding model
        """

        def decorator(model_class: Type[EmbeddingModel]) -> Type[EmbeddingModel]:
            if cls._models.get(name, None) is not None:
                raise ValueError(f"Embedding model {name} already registered")
            cls._models[name] = model_class
            return model_class

        return decorator

    @classmethod
    def get_model(cls, name: str) -> EmbeddingModel:
        """Get the embedding model by name."""
        return cls._models[name]()

    @classmethod
    def get_supported_models(cls) -> list[str]:
        """Get list of supported embedding models."""
        return list(cls._models.keys())

    @classmethod
    def is_supported(cls, name: str) -> bool:
        """Check if an embedding model is supported."""
        return name in cls._models

class OpenAI(EmbeddingModel):
    """OpenAI embedding model."""
    def __init__(self, model_name: str):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = model_name
    
    def embed(self, text: str) -> np.ndarray:
        raise NotImplementedError("OpenAI embedding model is not implemented")

    def query(self, text: str) -> np.ndarray:
        response = requests.post(
            "https://api.openai.com/v1/embeddings",
            json={
                "model": self.model_name,
                "input": text
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]

@_EmbeddingModelRegistry.register("openai-text-embedding-3-small")
class OpenAITextEmbedding3Small(OpenAI):
    """OpenAI Text Embedding 3 Small embedding model."""
    def __init__(self):
        super().__init__(model_name="text-embedding-3-small")
    
    def embed(self, text: str) -> np.ndarray:
        return self.query(text)

@_EmbeddingModelRegistry.register("openai-text-embedding-3-large")
class OpenAITextEmbedding3Small(OpenAI):
    """OpenAI Text Embedding 3 Large embedding model."""
    def __init__(self):
        super().__init__(model_name="text-embedding-3-large")
    
    def embed(self, text: str) -> np.ndarray:
        return self.query(text)


def get_embedding_model(model_name: str) -> EmbeddingModel:
    """Get an embedding model by name."""
    if not _EmbeddingModelRegistry.is_supported(model_name):
        raise ValueError(f"Embedding model {model_name} not supported")
    return _EmbeddingModelRegistry.get_model(model_name)
