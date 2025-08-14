# rag/retriever.py

from __future__ import annotations

from typing import Any
from config import load_config
from langchain.chains import RetrievalQA

_OLLAMA_CLS = None
try:
    from langchain_ollama import OllamaLLM as _OLLAMA_CLS
except Exception:
    try:
        from langchain_community.llms import Ollama as _OLLAMA_CLS
    except Exception:
        _OLLAMA_CLS = None


def _cfg_get(obj: Any, name: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _build_ollama_llm(cfg: Any):
    if _OLLAMA_CLS is None:
        raise ImportError(
            "Ollama LLM integration not found. Install `langchain-ollama` or ensure "
            "`langchain_community.llms.Ollama` is available."
        )
    llm_cfg = _cfg_get(cfg, "llm", None)
    model = _cfg_get(llm_cfg, "model", "")
    base_url = _cfg_get(llm_cfg, "base_url", "http://localhost:11434")

    params = dict(_cfg_get(llm_cfg, "params", {}) or {})
    timeout = _cfg_get(llm_cfg, "request_timeout_s", None)
    if timeout is not None:
        params.setdefault("timeout", float(timeout))
    max_retries = _cfg_get(llm_cfg, "max_retries", None)
    if max_retries is not None:
        params.setdefault("max_retries", int(max_retries))
    headers = _cfg_get(llm_cfg, "headers", None)
    if headers:
        params.setdefault("headers", dict(headers))

    return _OLLAMA_CLS(model=model, base_url=base_url, **params)


def build_qa(
    retriever,
    cfg: Any = None,
    *,
    yaml_path: str = "config.yaml",
    use_yaml: bool = True,
) -> RetrievalQA | dict:
    """
    Build a RetrievalQA chain using config. If cfg is None, load config.
    """
    if cfg is None:
        cfg = load_config(yaml_path=yaml_path, use_yaml=use_yaml)

    llm_cfg = _cfg_get(cfg, "llm", None)

    if not _cfg_get(llm_cfg, "enabled", True):
        return {"ok": True, "llm": "disabled"}

    provider = str(_cfg_get(llm_cfg, "provider", "ollama")).lower()
    if provider != "ollama":
        raise ValueError(f"Unsupported LLM provider: {_cfg_get(llm_cfg, 'provider', '')}")

    llm = _build_ollama_llm(cfg)

    chain_type_kwargs = _cfg_get(llm_cfg, "chain_type_kwargs", None)

    kwargs = dict(
        llm=llm,
        chain_type=str(_cfg_get(llm_cfg, "chain_type", "stuff")),
        retriever=retriever,
        return_source_documents=True,
    )
    if chain_type_kwargs:
        kwargs["chain_type_kwargs"] = chain_type_kwargs

    return RetrievalQA.from_chain_type(**kwargs)
