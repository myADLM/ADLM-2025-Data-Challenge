# rag/rerankers/char_ngram.py

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Callable
import re
from rapidfuzz import fuzz

def _char_ngrams(s: str, n: int = 3) -> set[str]:
    s = re.sub(r"\s+", " ", s.lower())
    if len(s) <= n:
        return {s}
    return {s[i:i+n] for i in range(len(s)-n+1)}

def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / max(1, len(a | b))

def _minmax_norm(pairs: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
    if not pairs:
        return pairs
    vals = [s for _, s in pairs]
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    return [(i, (s - lo) / span) for i, s in pairs]

@dataclass
class CharNGramCfg:
    n: int = 3
    weight: float = 0.35
    jaccard_w: float = 0.6
    fuzz_w: float = 0.4

class CharNGramReranker:
    """Lightweight reranker using character n-grams and fuzzy matching."""
    def __init__(self, cfg: CharNGramCfg | None = None):
        self.cfg = cfg or CharNGramCfg()

    def rerank(
        self,
        query: str,
        candidates: List[Tuple[str, float]],
        id2text: Callable[[str], str],
    ) -> List[Tuple[str, float]]:
        if not candidates:
            return candidates
        qset = _char_ngrams(query, self.cfg.n)
        bm25_norm = _minmax_norm(candidates)
        out: List[Tuple[str, float]] = []
        ql = query.lower()
        for cid, s_norm in bm25_norm:
            text = id2text(cid)
            cset = _char_ngrams(text, self.cfg.n)
            j = _jaccard(qset, cset)
            fz = fuzz.partial_ratio(ql, text.lower()) / 100.0
            enrich = self.cfg.jaccard_w * j + self.cfg.fuzz_w * fz
            final = (1 - self.cfg.weight) * s_norm + self.cfg.weight * enrich
            out.append((cid, final))
        out.sort(key=lambda x: x[1], reverse=True)
        return out
