import time
from app.src.search.bm25 import BM25
from app.src.search.vector_search import VectorSearch
import polars as pl
import time

df = pl.read_parquet("app/database/medallions/silver.parquet")
#srch = BM25(df["chunk_text"], overwrite=False)
#
#t0 = time.time()
#srch.search("This is a test query to see how long it takes to search.")
#t1 = time.time()
#print(f"Search time: {t1-t0} seconds")

t0 = time.time()
srch = VectorSearch(df["chunk_text"], embedder="Quen3_8B", embedding_cache="app/database/embedding_cache")
t1 = time.time()
print(f"VectorSearch initialization time: {t1-t0} seconds")

t2 = time.time()
srch.search("This is a test query to see how long it takes to search.", n=10)
t3 = time.time()
print(f"Search time: {t3-t2} seconds")