"""
RAG query system using LlamaIndex abstractions for intelligent document Q&A.
"""
import argparse
from pathlib import Path
from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.bedrock_converse import BedrockConverse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def setup_llm():
    """Setup Bedrock LLM through LlamaIndex."""
    try:
        # Use Bedrock model from environment variable
        model_id = os.getenv("BEDROCK_MODEL_ID", "openai.gpt-oss-120b-1:0")
        aws_profile = os.getenv("AWS_PROFILE")
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        print(f"Using Bedrock model: {model_id} in region: {region}")
        
        llm = BedrockConverse(
            model=model_id,
            region_name=region,
            profile_name=aws_profile,
            temperature=0.1,
            max_tokens=1024
        )
        return llm
    except Exception as e:
        raise ValueError(f"Failed to setup Bedrock LLM: {e}")


def main():
    parser = argparse.ArgumentParser(description="Query indexed documents with natural language")
    parser.add_argument("--query", help="Question to ask about the documents")
    parser.add_argument("--persist-dir", default="./vectordb", help="Directory with vector DB")
    parser.add_argument("--top-k", type=int, default=5, help="Number of chunks to retrieve")
    
    args = parser.parse_args()
    
    print("🔧 Setting up RAG system...")
    
    # Setup embeddings (same as indexer)
    embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        trust_remote_code=True
    )
    Settings.embed_model = embed_model
    
    # Setup LLM
    try:
        llm = setup_llm()
        Settings.llm = llm
        model_id = os.getenv("BEDROCK_MODEL_ID", "openai.gpt-oss-120b-1:0")
        print(f"✅ LLM configured: {model_id} (Bedrock)")
    except Exception as e:
        print(f"❌ LLM setup failed: {e}")
        return
    
    # Load index
    persist_dir = Path(args.persist_dir)
    if not persist_dir.exists():
        print(f"❌ Index directory not found: {args.persist_dir}")
        print("Run indexer first: python src/labdocs/indexer.py")
        return
    
    print("📂 Loading document index...")
    storage_context = StorageContext.from_defaults(persist_dir=str(persist_dir))
    index = load_index_from_storage(storage_context)
    
    print("✅ RAG system ready!")
    print()
    
    # Create query engine using LlamaIndex abstractions
    print("🔍 Creating query engine...")
    query_engine = index.as_query_engine(
        similarity_top_k=args.top_k,
        verbose=True
    )
    
    def ask_question(question: str):
        print(f"❓ **Question:** {question}")
        print("-" * 60)
        
        try:
            # Query using LlamaIndex's high-level abstraction
            response = query_engine.query(question)
            
            print(f"🤖 **Answer:**")
            print(response.response)
            print()
            
            # Show source references
            if hasattr(response, 'source_nodes') and response.source_nodes:
                print(f"📚 **Sources ({len(response.source_nodes)} chunks retrieved):**")
                for i, node in enumerate(response.source_nodes, 1):
                    metadata = node.node.metadata
                    score = node.score if hasattr(node, 'score') else 0.0
                    filename = metadata.get('filename', 'Unknown')
                    filepath = metadata.get('filepath', 'Unknown')
                    
                    print(f"  {i}. **{filename}** (Score: {score:.3f})")
                    print(f"     Path: {filepath}")
                    
                    # Show preview of retrieved content
                    preview = node.node.text.replace('\n', ' ')[:200]
                    print(f"     Preview: {preview}...")
                    print()
            else:
                print("📚 **Sources:** No source information available")
                
        except Exception as e:
            print(f"❌ Error processing query: {e}")
    
    # Interactive or single query mode
    if args.query:
        ask_question(args.query)
    else:
        print("🔍 **Interactive Q&A Mode** (type 'quit' to exit)")
        print("Ask questions about your documents in natural language.")
        print()
        
        while True:
            try:
                question = input("❓ Your question: ").strip()
                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                if question:
                    print()
                    ask_question(question)
                    print("=" * 80)
                    print()
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break


if __name__ == "__main__":
    main()
