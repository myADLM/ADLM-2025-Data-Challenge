import os
from pathlib import Path

import numpy as np
from openai import OpenAI


class OpenAIAPI:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    def embed(
        self, text: str, cached: Path, model: str = "text-embedding-3-large"
    ) -> list[float]:
        if cached.exists():
            return np.load(cached)

        response = self.client.embeddings.create(input=text, model=model)
        embedding = np.asarray(response.data[0].embedding, dtype=np.float64)
        np.save(cached, embedding)
        return embedding
