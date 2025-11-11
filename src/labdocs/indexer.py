"""
Document indexer using LlamaIndex + SimpleVectorStore with hierarchy-preserving chunking.
"""
import argparse
import os
from pathlib import Path

from tqdm import tqdm
from dotenv import load_dotenv

from llama_index.core import Document, VectorStoreIndex, Settings, StorageContext, load_index_from_storage
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.bedrock import BedrockEmbedding


def init_embedding_model(embedding_model: str = "huggingface", aws_region: str = "us-east-1"):
    """Initialize embedding model based on user choice."""
    print(f"Loading the embedding model: {embedding_model}...")

    if embedding_model.lower() == "bedrock":
        embed_model = BedrockEmbedding(
            model_name="amazon.titan-embed-text-v2:0",
            region_name=aws_region,
            embed_batch_size=10
        )
        print(f"  Using Bedrock Titan embeddings (1024 dimensions, batch_size=10, max_tokens=1024)")
    else:
        embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            trust_remote_code=True
        )
        print(f"  Using HuggingFace SentenceTransformer (384 dimensions)")

    return embed_model


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Index markdown documents with hierarchy preservation")
    parser.add_argument("--input-folder", default=None, help="Folder with markdown files")
    parser.add_argument("--collection", default="lab_docs", help="Collection name")
    parser.add_argument("--persist-dir", default="./vectordb", help="Directory to persist vector DB")
    parser.add_argument("--max-docs", type=int, default=0, help="Maximum documents to process (0 = unlimited)")
    parser.add_argument("--embedding-model", choices=["huggingface", "bedrock"], default="huggingface",
                        help="Embedding model to use: huggingface or bedrock")
    parser.add_argument("--aws-region", default="us-east-1", help="AWS region for Bedrock")

    args = parser.parse_args()

    embed_model = init_embedding_model(args.embedding_model, args.aws_region)
    Settings.embed_model = embed_model
    
    
    input_path = Path(args.input_folder)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input folder not found: {input_path}")

    print(f"Loading documents [{input_path}]...")
    # Check for existing index to skip already processed documents
    persist_dir = Path(args.persist_dir)
    processed_files = set()
    
    if persist_dir.exists() and (persist_dir / "docstore.json").exists():
        print("Checking for already processed documents...")
        try:
            storage_context = StorageContext.from_defaults(persist_dir=str(persist_dir))
            existing_index = load_index_from_storage(storage_context)
            # Get processed filenames from existing nodes
            for node_id in existing_index.docstore.docs:
                node = existing_index.docstore.get_document(node_id)
                if node.metadata and "filename" in node.metadata:
                    processed_files.add(node.metadata["filename"])
            print(f"Found {len(processed_files)} already processed files")
        except:
            print("No existing index found, processing all documents")
    
    documents = []
    md_files = list(input_path.rglob("*.md"))
    
    # Filter out already processed files
    unprocessed_files = [f for f in md_files if f.name not in processed_files]
    
    if args.max_docs > 0:
        unprocessed_files = unprocessed_files[:args.max_docs]
    
    print(f"Processing {len(unprocessed_files)} new documents (skipped {len(processed_files)} already processed)")
    
    if not unprocessed_files:
        print("No new documents to process")
        return
    
    for md_file in unprocessed_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        doc = Document(
            text=content,
            metadata={
                "filename": md_file.name,
                "filepath": str(md_file.relative_to(input_path)),
                "source": str(md_file)
            }
        )
        documents.append(doc)
    
    print(f"Loaded {len(documents)} new documents")
    
    print("Chunking new documents...")
    node_parser = MarkdownNodeParser(
        include_metadata=True,
        include_prev_next_rel=True
    )
    nodes = node_parser.get_nodes_from_documents(documents, show_progress=True)
    
    # Enhance metadata with chunk information
    for i, node in enumerate(nodes):
        node.metadata.update({
            "chunk_id": i,
            "chunk_type": "markdown_section"
        })
    
    print(f"Created {len(nodes)} chunks")
    
    persist_dir.mkdir(exist_ok=True)
    
    # Load existing index or create new one
    if persist_dir.exists() and (persist_dir / "docstore.json").exists():
        print("Updating the vector index...")
        storage_context = StorageContext.from_defaults(persist_dir=str(persist_dir))
        index = load_index_from_storage(storage_context)
        
        # Add new nodes to existing index
        print("Adding new chunks...")
        for node in tqdm(nodes, desc="Adding chunks to index"):
            index.insert(node)
    else:
        print("Creating new index...")
        # Create vector store and storage context
        vector_store = SimpleVectorStore()
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # Create index
        index = VectorStoreIndex(
            nodes=nodes,
            storage_context=storage_context,
            show_progress=True
        )
    
    # Persist to disk
    index.storage_context.persist(persist_dir=str(persist_dir))
    
    print(f"Indexed {len(documents)} new documents with {len(nodes)} chunks")
    print(f"Saved to: {args.persist_dir}")


if __name__ == "__main__":
    main()