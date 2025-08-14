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
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field



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
    store_dir: str = ".rag_store"
    index_dirname: str = "index"
    manifest_filename: str = "manifest.sqlite"
    embed_cache_filename: str = "embed_cache.sqlite"
    journal_filename: str = "journal.log"
    lock_filename: str = ".rag.lock"
    tmp_dirname: str = "_tmp"

@dataclass
class HashingCfg:
    normalize: Optional[str] = "NFC"   # "NFC" | "NFKC" | None
    # Text encoding
    encoding: str = "utf-8"
    chunk_id_hash_len: int = 32

@dataclass
class JournalCfg:
    # Use an inter-process lock when writing the journal
    enable_lock: bool = True
    # Call fsync after each append (safer but slower). Default off.
    fsync_default: bool = False
    # Use compact JSON (no extra spaces)
    compact_json: bool = True
    # Max size in bytes for a single record. None = no limit.
    # If exceeded, "data" will be replaced by {"_truncated": True}.
    max_record_bytes: Optional[int] = None
    # Rotate when the file is bigger than this
    rotate_max_bytes: int = 10 * 1024 * 1024
    # How many rotated files to keep (journal.log.1..N)
    rotate_keep: int = 5
    # Default N for tail-like features (if you add one later)
    default_tail_n: int = 200

@dataclass
class LockCfg:
    # Max time to wait for the lock
    timeout_s: float = 30.0
    # First backoff sleep
    backoff_initial_s: float = 0.001
    # Max backoff sleep
    backoff_max_s: float = 0.05

@dataclass
class SqliteCfg:
    journal_mode: str = "WAL"        # "WAL" | "DELETE" | ...
    busy_timeout_ms: int = 30000     # 30s
    synchronous: str = "NORMAL"      # "OFF" | "NORMAL" | "FULL" | "EXTRA"
    connect_timeout_s: float = 1.0   # python sqlite3.connect(timeout=...)

@dataclass
class EmbedCacheCfg:
    table_name: str = "emb_cache"
    max_vars_fallback: int = 900
    reserve_bind_params: int = 16
    chunk_size_limit: Optional[int] = None
    json_ensure_ascii: bool = False
    json_separators: tuple[str, str] = (",", ":")

@dataclass
class PdfLoaderCfg:
    prefetch_budget_mb: int = 64
    io_batch_files: int = 8
    num_proc: str = "max"

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
    # Processes to use: integer or "max"
    num_proc: str | int = "max"
    # Metadata key priorities when extracting path/page
    source_keys: list[str] = field(default_factory=lambda: ["source", "file_path", "path"])
    page_keys: list[str] = field(default_factory=lambda: ["page", "page_number", "page_no"])



# Setting for the old sentence transformer all-MiniLM-L6-v2
@dataclass
class EmbeddingCfg:
    # Parameters for text embedding model
    model_name: str = (
        "./models/all-MiniLM-L6-v2"  # Name of the embedding model
    )
    embedding_dim: int = 384  # Size of the embedding vector (must match the model)
    batch_size: int = 64
    faiss_metric: str = "l2"  # "l2" or "ip"
    normalize_embeddings: bool = False # set true when faiss_metric is ip
    multi_gpu: object = False   # false | "auto" | [0,1]
    dtype: str = "float32"      # "float32" | "float16"
    pad_to_batch: bool = False  # steady throughput for multi-GPU
    in_queue_maxsize: int = 4   # per-GPU pending batches



# Setting for the new sentence transformer InstructorXL
# @dataclass
# class EmbeddingCfg:
#     # Parameters for text embedding model
#     model_name: str = (
#         "./models/InstructorXL"  # Name of the embedding model
#     )
#     embedding_dim: int = 768  # Size of the embedding vector (must match the model)
#     batch_size: int = 64
#     faiss_metric: str = "l2"  # "l2" or "ip"


@dataclass
class RetrieverCfg:
    # Search and retrieval settings
    search_type: str = "similarity"  # Retrieval strategy
    k: int = 4  # Number of results to return per query
    fetch_k: int = 50  # initial candidates for retrievers/rerankers

@dataclass
class FaissCfg:
    strict_meta_check: bool = True      # raise if meta mismatch
    clear_on_delete: bool = True        # delete_by_chunk_ids clears whole index
    normalize_query_in_ip: bool = True  # in ip mode, normalize query if callable


@dataclass
class LLMCfg:
    # Large Language Model (LLM) settings
    provider: str = "ollama"  # LLM provider or backend
    model: str = "deepseek-r1-8b-int8"  # Model name to be used by the provider
    chain_type: str = "stuff"
    base_url: str = "http://localhost:11434"
    params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ManagerCfg:
    enable_cache: bool = True
    enable_journal: bool = True
    hash_block_bytes: int = 1024 * 1024
    include_globs: List[str] = field(default_factory=list)
    exclude_globs: List[str] = field(default_factory=list)
    follow_symlinks: bool = False
    ignore_dotfiles: bool = True


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
    hashing: HashingCfg = field(default_factory=HashingCfg)
    journal: JournalCfg = field(default_factory=JournalCfg)
    lock: LockCfg = field(default_factory=LockCfg)
    sqlite: SqliteCfg = field(default_factory=SqliteCfg)
    embed_cache: EmbedCacheCfg = field(default_factory=EmbedCacheCfg)
    faiss: FaissCfg = field(default_factory=FaissCfg)
    pdf_loader: PdfLoaderCfg = field(default_factory=PdfLoaderCfg)
    manager: ManagerCfg = field(default_factory=ManagerCfg)


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


def load_config(yaml_path: Optional[str] = "config.yaml", use_yaml: bool = True) -> Config:
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
        if not key.upper().startswith("CONFIG__"):
            continue
        parts = key.split("__")[1:]  # Example: CONFIG__runtime__device -> ["runtime", "device"]
        target = cfg
        for seg in parts[:-1]:
            if not hasattr(target, "__dataclass_fields__"):
                target = None
                break
            fields = getattr(target, "__dataclass_fields__")
            name = {k.lower(): k for k in fields}.get(seg.lower())
            if name is None:
                target = None
                break
            target = getattr(target, name, None)

        if target is None:
            continue

        leaf = parts[-1]
        fields = getattr(target, "__dataclass_fields__", {})
        leaf_name = {k.lower(): k for k in fields}.get(leaf.lower())
        if leaf_name is None:
            continue

        old = getattr(target, leaf_name)
        if isinstance(old, bool):
            v = val.lower() in ("1", "true", "yes", "on")
        elif isinstance(old, int):
            v = int(val)
        elif isinstance(old, float):
            v = float(val)
        else:
            v = val
        setattr(target, leaf_name, v)


    return cfg


