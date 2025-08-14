# rag/retriever.py

from __future__ import annotations

from typing import Any
from langchain.chains import RetrievalQA

_OLLAMA_CLS = None
try:
    from langchain_ollama import OllamaLLM as _OLLAMA_CLS
except Exception:
    try:
        from langchain_community.llms import Ollama as _OLLAMA_CLS
    except Exception:
        _OLLAMA_CLS = None


def _build_ollama_llm(cfg):
    if _OLLAMA_CLS is None:
        raise ImportError(
            "Ollama LLM integration not found. Install `langchain-ollama` or ensure "
            "`langchain_community.llms.Ollama` is available."
        )
    params = dict(cfg.llm.params or {})
    # align common kwargs: model, base_url
    return _OLLAMA_CLS(model=cfg.llm.model, base_url=cfg.llm.base_url, **params)


def build_qa(retriever, cfg) -> RetrievalQA:
    """
    Build a RetrievalQA chain with the configured LLM provider.
    Currently supports: provider='ollama'.
    """
    provider = str(cfg.llm.provider).lower()
    if provider != "ollama":
        raise ValueError(f"Unsupported LLM provider: {cfg.llm.provider}")

    llm = _build_ollama_llm(cfg)
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type=str(cfg.llm.chain_type),
        retriever=retriever,
        return_source_documents=True,
    )
