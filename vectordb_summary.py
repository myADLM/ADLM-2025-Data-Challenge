#!/usr/bin/env python3
"""Display vector database (LlamaIndex) summary information."""
import json
import os
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

def get_vectordb_summary(vectordb_path: str) -> Dict:
    vectordb_path = Path(vectordb_path)

    summary = {
        "path": str(vectordb_path),
        "exists": vectordb_path.exists(),
        "embeddings": 0,
        "documents": 0,
        "unique_documents": 0,
        "metadata_entries": 0,
        "file_sizes": {},
        "index_info": {},
        "document_sources": defaultdict(int),
        "errors": []
    }

    if not vectordb_path.exists():
        summary["errors"].append(f"Path does not exist: {vectordb_path}")
        return summary

    # Check file sizes
    for file in vectordb_path.glob("*.json"):
        size_mb = file.stat().st_size / (1024 * 1024)
        summary["file_sizes"][file.name] = f"{size_mb:.2f} MB"

    # Analyze vector store
    vector_store_file = vectordb_path / "default__vector_store.json"
    if vector_store_file.exists():
        try:
            with open(vector_store_file) as f:
                vector_data = json.load(f)

            summary["embeddings"] = len(vector_data.get("embedding_dict", {}))
            summary["metadata_entries"] = len(vector_data.get("metadata_dict", {}))

            metadata = vector_data.get("metadata_dict", {})
            for entry_id, meta in metadata.items():
                if isinstance(meta, dict) and "filename" in meta:
                    summary["document_sources"][meta["filename"]] += 1
        except Exception as e:
            summary["errors"].append(f"Error reading vector store: {e}")

    # Analyze docstore
    docstore_file = vectordb_path / "docstore.json"
    if docstore_file.exists():
        try:
            with open(docstore_file) as f:
                docstore_data = json.load(f)

            ref_docs = docstore_data.get("docstore/ref_doc_info", {})
            summary["unique_documents"] = len(ref_docs)

            doc_data = docstore_data.get("docstore/data", {})
            summary["documents"] = len(doc_data)
        except Exception as e:
            summary["errors"].append(f"Error reading docstore: {e}")

    # Analyze index store
    index_store_file = vectordb_path / "index_store.json"
    if index_store_file.exists():
        try:
            with open(index_store_file) as f:
                index_data = json.load(f)

            index_info = index_data.get("index_store/data", {})
            summary["index_info"]["total_indexes"] = len(index_info)
            if index_info:
                summary["index_info"]["indexes"] = list(index_info.keys())[:5]
        except Exception as e:
            summary["errors"].append(f"Error reading index store: {e}")

    return summary


def print_summary(summary: Dict):
    print("=" * 80)
    print("VECTOR DATABASE SUMMARY")
    print("=" * 80)

    print(f"\nPath: {summary['path']}")
    print(f"Status: {'Available' if summary['exists'] else 'Not found'}")

    if not summary['exists']:
        print("\nDatabase does not exist at this location.")
        return

    print(f"\nEmbeddings: {summary['embeddings']}")
    print(f"Document Nodes: {summary['documents']}")
    print(f"Unique Documents: {summary['unique_documents']}")
    print(f"Metadata Entries: {summary['metadata_entries']}")

    print("\n" + "-" * 80)
    print("FILE SIZES:")
    print("-" * 80)
    for filename, size in sorted(summary["file_sizes"].items()):
        print(f"  {filename:30} {size:>12}")

    if summary["document_sources"]:
        print("\n" + "-" * 80)
        print("TOP DOCUMENT SOURCES:")
        print("-" * 80)
        sorted_sources = sorted(
            summary["document_sources"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        for filename, count in sorted_sources[:15]:
            print(f"  {filename:45} {count:5} embeddings")
        if len(sorted_sources) > 15:
            print(f"  ... and {len(sorted_sources) - 15} more sources")

    if summary["index_info"].get("total_indexes", 0) > 0:
        print("\n" + "-" * 80)
        print("INDEXES:")
        print("-" * 80)
        print(f"  Total Indexes: {summary['index_info']['total_indexes']}")
        if summary["index_info"].get("indexes"):
            for idx in summary["index_info"]["indexes"]:
                print(f"    - {idx}")

    if summary["errors"]:
        print("\n" + "-" * 80)
        print("ERRORS:")
        print("-" * 80)
        for error in summary["errors"]:
            print(f"  WARNING: {error}")

    print("\n" + "=" * 80)


def main():
    vectordbs = [
        "./vectordb",
        "./vectordb_bedrock",
        "./vectordb_huggingface",
    ]

    for db_path in vectordbs:
        summary = get_vectordb_summary(db_path)
        print_summary(summary)
        print()


if __name__ == "__main__":
    main()
