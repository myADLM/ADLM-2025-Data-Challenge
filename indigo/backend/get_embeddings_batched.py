import json, uuid, math, os
from pathlib import Path
from openai import OpenAI
import polars as pl

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

df = pl.read_parquet("app/database/medallions/silver.parquet")

texts = df["chunk_text"].to_list()
MODEL = "text-embedding-3-large"
CHUNK = 50000

batch_ids = []

for i in range(0, len(texts), CHUNK):
    part = texts[i:i+CHUNK]
    in_path = Path("tmp", f"embeddings_input_{i//CHUNK:03}.jsonl")
    with in_path.open("w", encoding="utf-8") as f:
        for t in part:
            f.write(json.dumps({
                "custom_id": f"emb-{uuid.uuid4()}",
                "method": "POST",
                "url": "/v1/embeddings",
                "body": {"model": MODEL, "input": t, "encoding_format": "float"}
            }) + "\n")

    file_obj = client.files.create(file=open(in_path, "rb"), purpose="batch")
    #batch = client.batches.create(
    #    input_file_id=file_obj.id,
    #    endpoint="/v1/embeddings",
    #    completion_window="24h",
    #    metadata={"shard": i//CHUNK}
    #)
    #batch_ids.append(batch.id)

with open("tmp/batch_ids.txt", "w") as f:
    f.write("\n".join(batch_ids))