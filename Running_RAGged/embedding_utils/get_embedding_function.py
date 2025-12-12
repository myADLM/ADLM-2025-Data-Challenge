from langchain_ollama import OllamaEmbeddings

def get_embedding_function(model_name: str = "llama3.1"):
    """Return embedding function for a given Ollama model."""
    return OllamaEmbeddings(model=model_name)