"""
RAG query system using LlamaIndex abstractions for intelligent document Q&A.
"""
import argparse
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.bedrock_converse import BedrockConverse
from botocore.exceptions import BotoCoreError, ClientError

# Import logger from kg_pipeline (shared logging)
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "kg_pipeline"))
from logger import setup_logger


# Model configuration
BEDROCK_MODEL_ID = "openai.gpt-oss-120b-1:0"
MAX_OUTPUT_TOKENS = 8000

# Initialize logger
logger = setup_logger("vectordb_pipeline.query")

# Load environment variables from .env file
load_dotenv()


def setup_llm() -> BedrockConverse:
    """
    Setup Bedrock LLM through LlamaIndex.
    
    Returns:
        BedrockConverse LLM instance
        
    Raises:
        ValueError: If AWS credentials are missing
        BotoCoreError: If AWS session/client creation fails
        ClientError: If Bedrock API call fails
    """
    try:
        # Use Bedrock model from environment variable
        model_id = os.getenv("BEDROCK_MODEL_ID", BEDROCK_MODEL_ID)
        aws_profile = os.getenv("AWS_PROFILE")
        aws_region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        
        if not aws_profile:
            raise ValueError(
                f"Missing AWS_PROFILE environment variable. "
                "Please set AWS_PROFILE in your .env file."
            )
        
        logger.info(f"Initializing Bedrock LLM (model: {model_id}, region: {aws_region})")
        
        llm = BedrockConverse(
            model=model_id,
            region_name=aws_region,
            profile_name=aws_profile,
            temperature=0.0,  # Deterministic output
            max_tokens=MAX_OUTPUT_TOKENS,
        )
        logger.info(f"Bedrock LLM initialized successfully")
        return llm
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise
    except (BotoCoreError, ClientError) as e:
        logger.error(f"AWS error initializing Bedrock LLM: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error setting up Bedrock LLM: {e}", exc_info=True)
        raise ValueError(f"Failed to setup Bedrock LLM: {e}")


def ask_question(question: str, query_engine) -> None:
    """
    Process a question using the RAG query engine.
    
    Args:
        question: User's question
        query_engine: LlamaIndex query engine instance
        
    Raises:
        ClientError: If Bedrock API call fails
        Exception: For other unexpected errors
    """
    print(f"**Question:** {question}")
    print("-" * 60)
    
    try:
        logger.info(f"Processing query: {question[:50]}...")
        # Query using LlamaIndex's high-level abstraction
        response = query_engine.query(question)
        
        print(f"**Answer:**")
        print(response.response)
        print()
        
        # Show source references
        if hasattr(response, 'source_nodes') and response.source_nodes:
            logger.info(f"Retrieved {len(response.source_nodes)} source chunks")
            print(f"**Sources ({len(response.source_nodes)} chunks retrieved):**")
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
            logger.warning("No source nodes found in response")
            print("**Sources:** No source information available")
            
    except ClientError as e:
        logger.error(f"Bedrock API error processing query: {e}")
        print(f"Error: Failed to generate response from Bedrock API: {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing query: {e}", exc_info=True)
        print(f"Error processing query: {e}")


def main() -> None:
    """Main RAG query function."""
    parser = argparse.ArgumentParser(description="Query indexed documents with natural language")
    parser.add_argument("--query", help="Question to ask about the documents")
    parser.add_argument("--persist-dir", default="./vectordb", help="Directory with vector DB")
    parser.add_argument("--top-k", type=int, default=5, help="Number of chunks to retrieve")
    
    args = parser.parse_args()
    
    logger.info("Setting up RAG system...")
    
    # Setup embeddings (same as indexer)
    try:
        embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            trust_remote_code=True
        )
        Settings.embed_model = embed_model
        logger.info("Embedding model initialized: sentence-transformers/all-MiniLM-L6-v2")
    except Exception as e:
        logger.error(f"Failed to initialize embedding model: {e}")
        raise
    
    # Setup LLM
    try:
        llm = setup_llm()
        Settings.llm = llm
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return
    except (BotoCoreError, ClientError) as e:
        logger.error(f"AWS error: {e}")
        return
    
    # Load index
    persist_dir = Path(args.persist_dir)
    if not persist_dir.exists():
        logger.error(f"Index directory not found: {args.persist_dir}")
        logger.info("Run indexer first: python src/labdocs/indexer.py")
        return
    
    logger.info("Loading document index...")
    try:
        storage_context = StorageContext.from_defaults(persist_dir=str(persist_dir))
        index = load_index_from_storage(storage_context)
        logger.info("Document index loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load index from {persist_dir}: {e}")
        raise
    
    logger.info("RAG system ready!")
    print()
    
    # Create query engine using LlamaIndex abstractions
    logger.info(f"Creating query engine (top_k={args.top_k})...")
    query_engine = index.as_query_engine(
        similarity_top_k=args.top_k,
        verbose=False  # Disable verbose to reduce noise, use logging instead
    )
    
    # Interactive or single query mode
    if args.query:
        ask_question(args.query, query_engine)
    else:
        logger.info("Starting interactive Q&A mode")
        print("**Interactive Q&A Mode** (type 'quit' to exit)")
        print("Ask questions about your documents in natural language.")
        print()
        
        while True:
            try:
                question = input("Your question: ").strip()
                if question.lower() in ['quit', 'exit', 'q']:
                    logger.info("User exited interactive mode")
                    print("Goodbye!")
                    break
                if question:
                    print()
                    ask_question(question, query_engine)
                    print("=" * 80)
                    print()
            except KeyboardInterrupt:
                logger.info("Session interrupted by user")
                print("\nGoodbye!")
                break
            except EOFError:
                logger.info("Session terminated")
                print("\nGoodbye!")
                break


if __name__ == "__main__":
    main()

