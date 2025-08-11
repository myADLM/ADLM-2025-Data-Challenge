# rag/hashing.py

import hashlib
import unicodedata
from typing import Final

UTF8: Final = "utf-8"

def sha256_bytes(data: bytes) -> str:
    # Hex SHA-256 of raw bytes.
    return hashlib.sha256(data).hexdigest()


def sha256_str(s: str, normalize: str | None = "NFC") -> str:
    # Hex SHA-256 of a string (UTF-8). Set None = "None" for better performance
    if normalize:
        s = unicodedata.normalize(normalize, s)
    return sha256_bytes(s.encode(UTF8))


