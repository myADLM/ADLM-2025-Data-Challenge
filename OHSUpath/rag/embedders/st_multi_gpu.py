# rag/embedders/st_multi_gpu.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Tuple
import os
import numpy as np
import multiprocessing as mp
from config import load_config


@dataclass
class STCfg:
    """
    Basic settings for the Sentence-Transformers embedder.

    Fields:
      model_name: Which ST model to load.
        e.g. "sentence-transformers/all-MiniLM-L6-v2"

      embedding_dim: Expected size of each embedding vector.
        Example: 384. Will validate this at runtime.

      batch_size: How many texts to encode at once.
        Bigger = faster, but needs more GPU/CPU memory. Start with 32 to 128.

      multi_gpu: Use more than one GPU?
        - False  : single CPU/GPU (default)
        - "auto" : use all visible GPUs (only if there are >= 2)
        - [0,2]  : pick specific GPU IDs by index

      normalize: If True, make each vector unit length (good for cosine similarity).

      dtype: Internal number type for arrays. Return type is still List[List[float]].
        - "float32" (safe default)
        - "float16" (uses less memory, tiny accuracy loss)

      pad_to_batch: If True, pad the last small batch so every batch has the same size.
        Can make multi-GPU throughput smoother. Slight extra work on the last batch.

      in_queue_maxsize: How many pending batches we allow per GPU.
        Lower  -> lower memory use, maybe less GPU utilization.
        Higher -> keeps GPUs busier, but needs more memory. Try 2 to 4.

      allow_cpu_fallback: If True, when CUDA init/transfer fails, fall back to CPU instead of raising.
    """
    model_name: str
    embedding_dim: int
    batch_size: int = 64
    multi_gpu: Any = False
    normalize: bool = False
    dtype: str = "float32"
    pad_to_batch: bool = False
    in_queue_maxsize: int = 4
    allow_cpu_fallback: bool = True


def _gpu_worker(
    dev_id: int,
    model_name: str,
    normalize: bool,
    batch_size: int,
    allow_cpu_fallback: bool,
    in_q: mp.Queue,
    out_q: mp.Queue,
    err_q: mp.Queue,
):
    """
    Single worker bound to one logical GPU. Uses a unified "safe load" policy:

    What it does:
      1) Read a job from 'in_q': (idxs, texts)
      2) Encode texts on its GPU with Sentence-Transformers
      3) Put results into 'out_q': (idxs, vectors)
      4) If it reads None from 'in_q', it exits

    Args:
      dev_id: CUDA device index for this worker (0-based).
      model_name: ST model to load on this GPU.
      normalize: Whether to normalize embeddings.
      batch_size: Number of texts per job for this worker.
      allow_cpu_fallback: Fall back to CPU if GPU not avaliable.
      in_q: Queue where the main process sends jobs.
      out_q: Queue where this worker sends back (idxs, embeddings).
      err_q: Queue to report exceptions so the main process can fail fast.
    """
    # Isolate the visible device for this worker before importing torch
    os.environ["CUDA_VISIBLE_DEVICES"] = str(dev_id)

    try:
        import torch
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(model_name, device="cpu")
        target_device = "cpu"

        try:
            if torch.cuda.is_available():
                model.to(torch.device("cuda"))
                target_device = "cuda"
        except Exception as e:
            if allow_cpu_fallback:
                print(f"[WARN][worker:{dev_id}] CUDA init/transfer failed; falling back to CPU: {repr(e)}")
                target_device = "cpu"
            else:
                raise

        while True:
            item = in_q.get()
            if item is None:
                break
            idxs, texts = item
            with torch.no_grad():
                try:
                    vecs = model.encode(
                        texts,
                        batch_size=batch_size,
                        convert_to_numpy=True,
                        normalize_embeddings=normalize,
                        show_progress_bar=False,
                        device=target_device,
                    )
                except TypeError:
                    vecs = model.encode(
                        texts,
                        batch_size=batch_size,
                        convert_to_numpy=True,
                        normalize_embeddings=normalize,
                        show_progress_bar=False,
                    )

            out_q.put((idxs, vecs.astype(np.float32, copy=False)))
    except Exception as e:
        # Surface errors to the main process; also unblock collectors
        try:
            err_q.put(repr(e))
            out_q.put(([], np.zeros((0,), dtype=np.float32)))
        except Exception:
            pass


class STMultiGPUEmbedder:
    """
    Sentence-Transformers embedder with a unified safety policy for both single and multi-GPU:
      - Always build the model on CPU first.
      - If device preference is "cuda", attempt to move to CUDA.
      - If that fails and allow_cpu_fallback=True: keep running on CPU; otherwise raise immediately.

    Device preference is read from config.runtime.device ("cuda" | "cpu").
    If runtime.device="cpu", multi_gpu is effectively disabled.
    """

    def __init__(self, cfg: STCfg | None = None):
        # ---- build cfg from file if not provided ----
        prefer_device: Optional[str] = None
        if cfg is None:
            app_cfg = load_config()
            emb = app_cfg.embedding
            cfg = STCfg(
                model_name=emb.model_name,
                embedding_dim=emb.embedding_dim,
                batch_size=emb.batch_size,
                multi_gpu=getattr(emb, "multi_gpu", False),
                normalize=getattr(emb, "normalize_embeddings", False),
                dtype=getattr(emb, "dtype", "float32"),
                pad_to_batch=getattr(emb, "pad_to_batch", False),
                in_queue_maxsize=getattr(emb, "in_queue_maxsize", 4),
                allow_cpu_fallback=getattr(emb, "allow_cpu_fallback", True),
            )
            prefer_device = getattr(getattr(app_cfg, "runtime", None), "device", None)
        else:
            try:
                prefer_device = getattr(getattr(load_config(), "runtime", None), "device", None)
            except Exception:
                prefer_device = None

        self.cfg = cfg
        self.model_name = cfg.model_name
        self.embedding_dim = int(cfg.embedding_dim)
        self.dtype = np.float16 if str(cfg.dtype).lower() == "float16" else np.float32
        self._allow_cpu_fallback = bool(getattr(cfg, "allow_cpu_fallback", True))

        # Respect device preference strictly; do not silently override it unless fallback is triggered.
        pref = (prefer_device or "").strip().lower()
        self._device_pref = "cuda" if pref == "cuda" else "cpu"

        # Internal fields
        self._model = None                      # single path model
        self._device_actual = "cpu"             # where the single path encodes on (after safe load)
        self._gpus: List[int] = self._resolve_gpus(cfg.multi_gpu)  # resolved multi-GPU ids (>=2) or []
        self._mpctx: Optional[mp.context.BaseContext] = None
        self._in_qs: List[mp.Queue] = []
        self._out_q: Optional[mp.Queue] = None
        self._err_q: Optional[mp.Queue] = None
        self._workers: List[mp.Process] = []

        if len(self._gpus) > 1:
            self._ensure_workers()
        else:
            self._load_single_model()

    # ---------- helpers ----------

    def _resolve_gpus(self, multi_gpu: Any) -> List[int]:
        """Return a list of GPU ids for multi-GPU mode; empty if single-path is used."""
        # If user prefers CPU, don't even try multi-GPU.
        if self._device_pref != "cuda":
            return []
        try:
            import torch
            has = bool(getattr(torch, "cuda", None) and torch.cuda.is_available())
            n = torch.cuda.device_count() if has else 0
        except Exception:
            n = 0

        if not multi_gpu or n == 0:
            return []
        if multi_gpu == "auto":
            return list(range(n)) if n >= 2 else []
        if isinstance(multi_gpu, (list, tuple)):
            out = [int(x) for x in multi_gpu if 0 <= int(x) < n]
            return out if len(out) >= 2 else []
        return []

    def _load_single_model(self):
        """Load a single SentenceTransformer model safely and decide the actual device."""
        if self._model is not None:
            return
        try:
            import torch
            from sentence_transformers import SentenceTransformer

            # Always build on CPU first to avoid meta-tensor surprises.
            model = SentenceTransformer(self.model_name, device="cpu")
            target = "cpu"

            # If user prefers CUDA, attempt to transfer. Fallback to CPU if allowed.
            if self._device_pref == "cuda":
                try:
                    if torch.cuda.is_available():
                        model.to(torch.device("cuda"))
                        target = "cuda"
                    else:
                        # CUDA not available: decide based on fallback policy
                        if self._allow_cpu_fallback:
                            print("[WARN] CUDA not available; falling back to CPU.")
                            target = "cpu"
                        else:
                            raise RuntimeError("CUDA not available and CPU fallback disabled.")
                except Exception as e:
                    if self._allow_cpu_fallback:
                        print(f"[WARN] CUDA init/transfer failed; falling back to CPU: {repr(e)}")
                        target = "cpu"
                    else:
                        raise

            self._model = model
            self._device_actual = target

        except Exception as e:
            raise RuntimeError(f"Failed to load SentenceTransformer: {e!r}")

        # Validate embedding dimension
        dim_fn = getattr(self._model, "get_sentence_embedding_dimension", None)
        if callable(dim_fn):
            dim = int(dim_fn())
            if dim != self.embedding_dim:
                raise ValueError(
                    f"Embedding dim mismatch: model={dim}, cfg.embedding_dim={self.embedding_dim}"
                )

    def _ensure_workers(self):
        """(Re)start multi-GPU workers with the unified safe policy."""
        if self._workers and all(p.is_alive() for p in self._workers):
            return
        # restart cleanly
        self.close()

        self._mpctx = mp.get_context("spawn")
        self._out_q = self._mpctx.Queue()
        self._err_q = self._mpctx.Queue()
        self._in_qs = []
        self._workers = []

        qsize = max(1, int(self.cfg.in_queue_maxsize))
        for dev in self._gpus:
            q = self._mpctx.Queue(maxsize=qsize)
            self._in_qs.append(q)
            p = self._mpctx.Process(
                target=_gpu_worker,
                args=(
                    dev,
                    self.model_name,
                    self.cfg.normalize,
                    int(self.cfg.batch_size),
                    bool(self._allow_cpu_fallback),
                    q,
                    self._out_q,
                    self._err_q,
                ),
                daemon=True,
            )
            p.start()
            self._workers.append(p)

    # ---------- public API ----------

    @property
    def device(self) -> str:
        """Return the actual device used by the single-path model ('cpu' or 'cuda')."""
        return self._device_actual

    def embed(self, texts):
        """
        Accepts:
        - str        -> returns List[float]
        - List[str]  -> returns List[List[float]]
        - []         -> returns []
        Routes:
        - multi-GPU  -> _embed_multi
        - single-GPU -> _embed_single
        """
        if isinstance(texts, list) and len(texts) == 0:
            return []

        single = isinstance(texts, str)
        texts_list = [texts] if single else list(texts)

        if len(getattr(self, "_gpus", []) or []) > 1:
            self._ensure_workers()
            vecs = self._embed_multi(texts_list)   # -> List[List[float]]
        else:
            self._load_single_model()
            vecs = self._embed_single(texts_list)  # -> List[List[float]]

        return vecs[0] if single else vecs



    def close(self):
        """Neatly stop workers and release resources."""
        if not self._workers:
            return
        try:
            for q in self._in_qs:
                q.put(None)
            for p in self._workers:
                p.join(timeout=10)
            for p in self._workers:
                if p.is_alive():
                    p.terminate()
        finally:
            self._workers.clear()
            self._in_qs.clear()
            if self._out_q is not None:
                try:
                    self._out_q.close()
                except Exception:
                    pass
            if self._err_q is not None:
                try:
                    self._err_q.close()
                except Exception:
                    pass
            self._out_q = None
            self._err_q = None

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    # ---------- impl ----------

    def _embed_single(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        import torch  # local import to avoid side effects at import time

        bs = max(1, int(self.cfg.batch_size))
        try:
            vecs = self._model.encode(
                texts,
                batch_size=bs,
                convert_to_numpy=True,
                normalize_embeddings=self.cfg.normalize,
                show_progress_bar=False,
                device=self._device_actual,  # new API
            )
        except TypeError:
            # old API fallback (relies on model's internal device)
            vecs = self._model.encode(
                texts,
                batch_size=bs,
                convert_to_numpy=True,
                normalize_embeddings=self.cfg.normalize,
                show_progress_bar=False,
            )

        if getattr(vecs, "ndim", None) == 1:
            vecs = vecs.reshape(1, -1)

        vecs = vecs.astype(self.dtype, copy=False)
        if vecs.ndim != 2 or vecs.shape[1] != self.embedding_dim:
            raise ValueError(f"Embedding dim mismatch: got {tuple(vecs.shape)}, expected (*, {self.embedding_dim})")
        return vecs.tolist()

    def _embed_multi(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        real_n = len(texts)
        batch = max(1, int(self.cfg.batch_size))

        # Optional padding for steadier throughput
        pad = 0
        if self.cfg.pad_to_batch:
            pad = (-real_n) % batch
            if pad:
                texts = texts + [""] * pad

        # Build tasks
        tasks: List[Tuple[List[int], List[str]]] = []
        for i in range(0, len(texts), batch):
            idxs = list(range(i, min(i + batch, len(texts))))
            tasks.append((idxs, texts[i:i + batch]))

        # Round-robin submit
        for j, t in enumerate(tasks):
            self._in_qs[j % len(self._gpus)].put(t)

        # Collect with safety
        import queue as pyqueue

        out: dict[int, np.ndarray] = {}
        remaining = len(tasks)
        while remaining:
            # bubble up worker errors quickly
            if self._err_q is not None:
                try:
                    msg = self._err_q.get_nowait()
                    raise RuntimeError(f"Worker error: {msg}")
                except pyqueue.Empty:
                    pass

            try:
                idxs, vecs = self._out_q.get(timeout=60.0)  # safety timeout
            except pyqueue.Empty:
                dead = [p for p in self._workers if not p.is_alive()]
                if dead:
                    raise RuntimeError("One or more GPU workers died unexpectedly.")
                continue

            for k, row in zip(idxs, vecs):
                out[k] = row.astype(self.dtype, copy=False)
            remaining -= 1

        # Order by original indices
        missing = [i for i in range(len(texts)) if i not in out]
        if missing:
            head = ", ".join(map(str, missing[:10]))
            raise RuntimeError(f"Missing embeddings for indices: {head}{'...' if len(missing)>10 else ''}")
        ordered = [out[i] for i in range(len(texts))]

        # Drop padded tail outputs
        if pad:
            ordered = ordered[:real_n]

        # Sanity check on one vector
        if ordered and (ordered[0].ndim != 1 or ordered[0].shape[0] != self.embedding_dim):
            raise ValueError(
                f"Embedding dim mismatch: got {ordered[0].shape[0]}, expected {self.embedding_dim}"
            )
        return [v.tolist() for v in ordered]
