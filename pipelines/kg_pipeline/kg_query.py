"""
Query laboratory SOP knowledge graph using PropertyGraphIndex.
Uses Neo4j graph store + SimpleVectorStore for semantic retrieval.
"""
import argparse
import os
from pathlib import Path
from dotenv import load_dotenv

from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.llms.bedrock_converse import BedrockConverse
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.core.indices.property_graph import PropertyGraphIndex
from llama_index.core import StorageContext, Settings
from botocore.exceptions import BotoCoreError, ClientError
from neo4j.exceptions import ServiceUnavailable, AuthError

from logger import setup_logger

logger = setup_logger("kg_pipeline.query")


def initialize_components():
    """Initialize all components: LLM, embeddings, graph store, vector store."""
    load_dotenv()

    aws_region = os.getenv("AWS_REGION")
    aws_profile = os.getenv("AWS_PROFILE")

    llm = BedrockConverse(
        model="openai.gpt-oss-120b-1:0",
        region_name=aws_region,
        profile_name=aws_profile,
        max_tokens=4096,
        temperature=0.0,
    )

    embed_model = BedrockEmbedding(
        model_name="amazon.titan-embed-text-v1",
        region_name=aws_region,
        profile_name=aws_profile,
    )
    Settings.embed_model = embed_model

    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USER")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    neo4j_database = os.getenv("NEO4J_DATABASE", "neo4j")

    if not neo4j_uri or not neo4j_user or not neo4j_password:
        raise ValueError("Missing Neo4j credentials")

    graph_store = Neo4jPropertyGraphStore(
        username=neo4j_user,
        password=neo4j_password,
        url=neo4j_uri,
        database=neo4j_database,
    )

    # Load vector store
    vector_dir = Path("./graphdb_vectorstore")
    if not vector_dir.exists():
        raise FileNotFoundError(
            f"Vector store not found at {vector_dir}. "
            "Run 02_load.py first to generate embeddings."
        )

    storage_context = StorageContext.from_defaults(persist_dir=str(vector_dir))

    logger.info("Initialized LLM, embeddings, graph store, and vector store")
    return llm, embed_model, graph_store, storage_context


def main():
    parser = argparse.ArgumentParser(
        description="Query laboratory SOP knowledge graph with semantic retrieval"
    )
    parser.add_argument(
        "--query",
        help="Question to ask (if not provided, runs in interactive mode)",
    )
    args = parser.parse_args()

    try:
        llm, embed_model, graph_store, storage_context = initialize_components()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return
    except FileNotFoundError as e:
        logger.error(f"Setup error: {e}")
        return
    except (BotoCoreError, ClientError, ServiceUnavailable, AuthError) as e:
        logger.error(f"Initialization error: {e}")
        return

    try:
        logger.info("Creating PropertyGraphIndex from existing graph...")
        index = PropertyGraphIndex.from_existing(
            property_graph_store=graph_store,
            storage_context=storage_context,
            embed_model=embed_model,
            llm=llm,
        )
        logger.info("PropertyGraphIndex created successfully")
    except Exception as e:
        logger.error(f"Failed to create PropertyGraphIndex: {e}", exc_info=True)
        return

    def query_graph(question: str) -> str:
        """Query the graph using semantic search + LLM synthesis."""
        try:
            # Get vector store from storage context
            vector_store = storage_context.vector_store

            # Generate query embedding
            query_embedding = embed_model.get_text_embedding(question)

            # Search vector store using VectorStoreQuery
            from llama_index.core.vector_stores.types import VectorStoreQuery

            query = VectorStoreQuery(
                query_embedding=query_embedding,
                similarity_top_k=10,
            )
            result = vector_store.query(query)

            context_text = "No relevant context found in knowledge base."

            if result is not None and result.ids is not None and len(result.ids) > 0:
                logger.info(f"Retrieved {len(result.ids)} similar embeddings")

                # Get metadata for retrieved nodes
                context_items = []
                for node_id in result.ids[:10]:
                    if node_id in vector_store.data.metadata_dict:
                        metadata = vector_store.data.metadata_dict[node_id]
                        entity_id = metadata.get('entity_id', node_id)
                        entity_type = metadata.get('entity_type', 'Unknown')
                        # Format context with available information
                        context_items.append(
                            f"- [{entity_type}] {entity_id}"
                        )

                if context_items:
                    context_text = "\n".join(context_items)
                    logger.info(f"Formatted {len(context_items)} context items")
            else:
                logger.warning("Vector store query returned no results")

            # Generate response using LLM
            prompt = f"""You are a laboratory informatics expert. Answer the following question using ONLY the provided context.

Question: {question}

Context from knowledge base:
{context_text}

Answer based on the context. If the information is not in the context, say so."""

            response = llm.complete(prompt)
            return response.text if hasattr(response, "text") else str(response)

        except Exception as e:
            logger.error(f"Query error: {e}", exc_info=True)
            raise

    print("=" * 70)
    print("LABORATORY SOP KNOWLEDGE BASE QUERY SYSTEM")
    print("(PropertyGraphIndex with Semantic Retrieval)")
    print("=" * 70)

    if args.query:
        logger.info(f"Processing query: {args.query[:50]}...")
        try:
            response = query_graph(args.query)
            print(f"\nQuestion: {args.query}")
            print("-" * 70)
            print(f"Answer:\n{response}\n")
        except Exception as e:
            print(f"\nError: {e}\n")
    else:
        logger.info("Entering interactive mode")
        print("\nInteractive Query Mode (type 'exit' or 'quit' to exit)")
        print()

        while True:
            try:
                question = input("Query> ").strip()

                if question.lower() in ["exit", "quit", "q"]:
                    print("Goodbye!")
                    break

                if not question:
                    continue

                try:
                    response = query_graph(question)
                    print(f"\nAnswer:\n{response}\n")
                except Exception as e:
                    print(f"Error: {e}\n")

                print("-" * 70)
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                break


if __name__ == "__main__":
    main()
