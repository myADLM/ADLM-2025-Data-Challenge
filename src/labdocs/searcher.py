"""
Document searcher using LlamaIndex + SimpleVectorStore with source tracking.
"""
import argparse
from pathlib import Path
from llama_index.core import VectorStoreIndex, Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


def main():
    parser = argparse.ArgumentParser(description="Search indexed documents")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--collection", default="lab_docs", help="Collection name")
    parser.add_argument("--persist-dir", default="./vectordb", help="Directory with vector DB")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results")
    
    args = parser.parse_args()
    
    print("Loading search index...")
    embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        trust_remote_code=True
    )
    Settings.embed_model = embed_model
    
    persist_dir = Path(args.persist_dir)
    if not persist_dir.exists():
        print(f"Index directory not found: {args.persist_dir}")
        print("Run indexer first: python src/labdocs/indexer.py <input_folder>")
        return
    
    # Load index from storage
    storage_context = StorageContext.from_defaults(persist_dir=str(persist_dir))
    index = load_index_from_storage(storage_context)
    print("Index loaded")
    
    def do_search(query: str):
        retriever = index.as_retriever(similarity_top_k=args.top_k)
        results = retriever.retrieve(query)
        
        print(f"\nQuery: '{query}'")
        print("-" * 50)
        
        if not results:
            print("No results found.")
            return
        
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            metadata = result.node.metadata
            score = result.score if hasattr(result, 'score') else 0.0
            preview = result.node.text.replace('\n', ' ')[:150]
            
            print(f"\n{i}. {metadata.get('filename', 'Unknown')} (Score: {score:.3f})")
            print(f"   Source: {metadata.get('filepath', 'Unknown')}")
            print(f"   Chunk: {metadata.get('chunk_id', 'N/A')}")
            print(f"   Preview: {preview}...")
    
    if args.query:
        do_search(args.query)
    else:
        print("\nInteractive search mode (type 'quit' to exit)")
        while True:
            query = input("\nQuery: ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            if query:
                do_search(query)


if __name__ == "__main__":
    main()