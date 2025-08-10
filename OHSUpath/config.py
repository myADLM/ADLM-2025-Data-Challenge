# config.py


# =============================================================
#   DEVELOPERS ONLY
#  WHO CAN EDIT THIS FILE:
#       Developers: to add new config fields or change default values
#       End users / Non-developers: DO NOT EDIT
#
#  NORMAL USERS:
#       Edit config.yaml instead to adjust program behavior.
#
#  HOW SETTINGS ARE USED:
#      1. Start with the settings stored in THIS file (default values).
#      2. If the same setting exists in config.yaml, USE THE SETTING STORED IN config.yaml.
#      3. If the same setting exists in environment variables,
#         USE THE SETTING STORED IN the environment variables (highest priority).
#
#  RESULT (priority order):
#      Environment variables (running in code) > config.yaml > defaults in config.py
#
#
#  ABOUT USE_YAML_CONFIG (defined in app.py):
#      - True  → Environment vars > config.yaml > defaults in config.py
#      - False → Environment vars > defaults in config.py   (YAML file is ignored)
#
#  EXAMPLES when USE_YAML_CONFIG = True:
#      Example 1:
#          default in config.py: 3
#          config.yaml:          2
#          env var:              1
#          → Program will use:   1  (from environment variables)
#
#      Example 2:
#          default in config.py: 3
#          config.yaml:          2
#          env var:            (none)
#          → Program will use:   2  (from config.yaml)
#
#  EXAMPLES when USE_YAML_CONFIG = False:
#      Example 3:
#          default in config.py: 3
#          config.yaml:          2
#          env var:              1
#          → Program will use:   1  (from environment variables)
#
#      Example 4:
#          default in config.py: 3
#          config.yaml:          2
#          env var:            (none)
#          → Program will use:   3  (from config.py)
# =============================================================


from dataclasses import dataclass, field, asdict, replace
from pathlib import Path
import os
import yaml
from typing import Optional, Dict, Any, List


# ----------------------------
# Section: Configuration Models
# ----------------------------

@dataclass
class AppUICfg:
    input_label: str = "***Enter your question***"
    spinner_text: str = "analysing..."

@dataclass
class AppCfg:
    title: str = "AI tool name holder"
    page_title: str = "AI tool name holder"
    ui: AppUICfg = field(default_factory=AppUICfg)

@dataclass
class PathsCfg:
    # Locations of important files and directories
    data_dir: str = "minidata/LabDocs"  # Set to minidata folder for faster initialization
    allowed_extensions: List[str] = field(default_factory=lambda: [".pdf"])
    pdf_text_mode: str = "text"  # "text" | "blocks" | "html"


@dataclass
class RuntimeCfg:
    # General runtime behaviour and system resource usage
    min_threads: int = 8  # Minimum number of worker threads to use
    reserve_threads: int = (
        2  # Threads to keep free for the operating system or other tasks
    )
    max_workers: Optional[int] = None
    device: str = "cuda"  # "cuda" or "cpu"

@dataclass
class SplitCfg:
    # Parameters for splitting documents into chunks
    chunk_size: int = 1200  # Target number of characters in each chunk
    chunk_overlap: int = (
        200  # Number of overlapping characters between consecutive chunks
    )
    min_chars_per_page: int = 1



@dataclass
class EmbeddingCfg:
    # Parameters for text embedding model
    model_name: str = (
        "sentence-transformers/all-MiniLM-L6-v2"  # Name of the embedding model
    )
    embedding_dim: int = 384  # Size of the embedding vector (must match the model)
    batch_size: int = 64
    faiss_metric: str = "l2"  # "l2" or "ip"



@dataclass
class RetrieverCfg:
    # Search and retrieval settings
    search_type: str = "similarity"  # Retrieval strategy
    k: int = 4  # Number of results to return per query


@dataclass
class LLMCfg:
    # Large Language Model (LLM) settings
    provider: str = "ollama"  # LLM provider or backend
    model: str = "deepseek-r1-8b-int8"  # Model name to be used by the provider
    chain_type: str = "stuff"
    base_url: str = "http://localhost:11434"
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Config:
    # Main configuration container combining all sections
    app: AppCfg = field(default_factory=AppCfg)
    paths: PathsCfg = field(default_factory=PathsCfg)
    runtime: RuntimeCfg = field(default_factory=RuntimeCfg)
    split: SplitCfg = field(default_factory=SplitCfg)
    embedding: EmbeddingCfg = field(default_factory=EmbeddingCfg)
    retriever: RetrieverCfg = field(default_factory=RetrieverCfg)
    llm: LLMCfg = field(default_factory=LLMCfg)
    app: AppCfg = field(default_factory=AppCfg)


# ----------------------------
# Section: Helper Functions
# ----------------------------


def _merge_dataclass(dc, overrides: Dict[str, Any]):
    """
    Recursively update a dataclass instance with values from a dictionary.
    If a field is itself a dataclass and the override is a dictionary,
    this function will merge them recursively.
    """
    for k, v in (overrides or {}).items():
        if hasattr(dc, k):
            cur = getattr(dc, k)
            if hasattr(cur, "__dataclass_fields__") and isinstance(v, dict):
                _merge_dataclass(cur, v)
            else:
                setattr(dc, k, v)


def load_config(
    yaml_path: Optional[str] = "config.yaml", use_yaml: bool = True
) -> Config:
    """
    Load the application configuration.

    Args:
        yaml_path: Path to a YAML file containing configuration overrides.
        use_yaml: If True, load settings from the YAML file (if it exists).
                  If False, only use Python defaults.

    Environment Variable Overrides:
        Any setting can be overridden via environment variables using the format:
        CONFIG__section__field=value
        Example:
            CONFIG__runtime__device=cpu
        This would set runtime.device to "cpu".

    Returns:
        Config: A fully populated Config object.
    """
    cfg = Config()

    # Load from YAML if enabled and file exists
    if use_yaml and yaml_path and Path(yaml_path).exists():
        with open(yaml_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        _merge_dataclass(cfg, raw)

    # Apply overrides from environment variables
    for key, val in os.environ.items():
        if not key.startswith("CONFIG__"):
            continue
        parts = key.split("__")[
            1:
        ]  # Example: CONFIG__runtime__device -> ["runtime", "device"]
        target = cfg
        for p in parts[:-1]:
            target = getattr(target, p, None)
            if target is None:
                break
        leaf = parts[-1]
        if target is not None and hasattr(target, leaf):
            old = getattr(target, leaf)
            if isinstance(old, bool):
                v = val.lower() in ("1", "true", "yes", "on")
            elif isinstance(old, int):
                v = int(val)
            else:
                v = val
            setattr(target, leaf, v)

    return cfg
