import os
from pathlib import Path
from typing import Dict, List, Any, Optional

from dotenv import load_dotenv
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.llms.bedrock_converse import BedrockConverse
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core import StorageContext
from neo4j.exceptions import ServiceUnavailable, AuthError

load_dotenv()


def get_graph_store() -> Neo4jPropertyGraphStore:
    """
    Get Neo4j graph store with credentials from environment variables.

    Returns:
        Neo4jPropertyGraphStore instance

    Raises:
        ValueError: If Neo4j credentials are missing
        ServiceUnavailable: If Neo4j connection fails
        AuthError: If Neo4j authentication fails
    """
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    database = os.getenv("NEO4J_DATABASE", "neo4j")

    if not uri or not username or not password:
        raise ValueError(
            "Missing required Neo4j environment variables. Please set NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD in your .env file"
        )

    try:
        graph_store = Neo4jPropertyGraphStore(
            username=username,
            password=password,
            url=uri,
            database=database,
        )
        return graph_store
    except (ServiceUnavailable, AuthError) as e:
        raise ValueError(f"Neo4j connection error: {e}")


def get_bedrock_llm() -> BedrockConverse:
    """
    Initialize Bedrock LLM for knowledge graph querying.

    Returns:
        BedrockConverse instance

    Raises:
        ValueError: If AWS credentials are missing
        Exception: If LLM initialization fails
    """
    aws_profile = os.getenv("AWS_PROFILE")
    aws_region = os.getenv("AWS_REGION")
    model_id = os.getenv("BEDROCK_MODEL_ID", "ai21.jamba-1-5-large-v1:0")

    if not aws_profile or not aws_region:
        raise ValueError(
            f"Missing AWS credentials. AWS_PROFILE={aws_profile}, AWS_REGION={aws_region}. "
            "Please set both in your .env file."
        )

    try:
        llm = BedrockConverse(
            model=model_id,
            region_name=aws_region,
            profile_name=aws_profile,
            temperature=0.1,
            max_tokens=2048
        )
        return llm
    except Exception as e:
        raise ValueError(f"Failed to initialize Bedrock LLM: {e}")


def get_embed_model() -> BedrockEmbedding:
    """
    Initialize Bedrock embedding model.

    Returns:
        BedrockEmbedding instance

    Raises:
        ValueError: If AWS credentials are missing
        Exception: If embedding model initialization fails
    """
    aws_profile = os.getenv("AWS_PROFILE")
    aws_region = os.getenv("AWS_REGION")

    if not aws_profile or not aws_region:
        raise ValueError(
            f"Missing AWS credentials. AWS_PROFILE={aws_profile}, AWS_REGION={aws_region}. "
            "Please set both in your .env file."
        )

    try:
        embed_model = BedrockEmbedding(
            model_name="amazon.titan-embed-text-v2:0",
            region_name=aws_region,
            profile_name=aws_profile,
        )
        return embed_model
    except Exception as e:
        raise ValueError(f"Failed to initialize Bedrock embedding model: {e}")


def get_vector_store(vector_dir: Path = None) -> tuple[SimpleVectorStore, Path]:
    """Load or create vector store for entity embeddings."""
    if vector_dir is None:
        vector_dir = Path("./graphdb_vectorstore")
    vector_dir.mkdir(parents=True, exist_ok=True)

    try:
        storage_context = StorageContext.from_defaults(persist_dir=str(vector_dir))
        vector_store = storage_context.vector_store
    except Exception:
        vector_store = SimpleVectorStore(stores_text=True)

    return vector_store, vector_dir


def retrieve_context_from_graph(
    query: str,
    graph_store: Neo4jPropertyGraphStore,
    limit: int = 20
) -> Dict[str, List[str]]:
    """
    Retrieve entities and relationships from the knowledge graph based on a query.

    Uses semantic search with embeddings to find relevant entities and their relationships.

    Args:
        query: User query string
        graph_store: Neo4j graph store instance
        limit: Maximum number of entities to retrieve

    Returns:
        Dictionary with:
        - 'entities': List of entity names
        - 'relationships': List of relationship strings in format "source -[rel_type]-> target"
    """
    entities = []
    relationships = set()

    try:
        with graph_store._driver.session() as session:
            # Strategy 1: Find entities by text matching on query keywords
            keywords = [w for w in query.lower().split() if len(w) > 3]

            if keywords:
                # Search for entities whose name contains any query keyword
                keyword_pattern = '|'.join(keywords)
                search_query = f"""
                MATCH (n)
                WHERE n.name IS NOT NULL
                AND (
                    {' OR '.join([f'n.name =~ "(?i).*{kw}.*"' for kw in keywords[:5]])}
                )
                RETURN DISTINCT n.name as entity_name
                LIMIT $limit
                """

                try:
                    result = session.run(search_query, limit=limit)
                    for record in result:
                        entity_name = record.get("entity_name")
                        if entity_name and entity_name not in entities:
                            entities.append(entity_name)
                except Exception:
                    pass

            # Strategy 2: If keyword search didn't find enough, do semantic search with embeddings
            if len(entities) < limit // 2:
                try:
                    embed_model = get_embed_model()
                    query_embedding = embed_model.get_text_embedding(query)

                    # Get all entities with embeddings
                    embedding_query = """
                    MATCH (n)
                    WHERE n.embedding IS NOT NULL
                    AND n.name IS NOT NULL
                    RETURN n.name as entity_name, n.embedding as embedding
                    LIMIT 100
                    """

                    result = session.run(embedding_query)
                    scored_entities = []

                    for record in result:
                        entity_name = record.get("entity_name")
                        stored_embedding = record.get("embedding")

                        if entity_name and stored_embedding:
                            # Calculate similarity (simple dot product)
                            similarity = sum(a * b for a, b in zip(query_embedding, stored_embedding))
                            scored_entities.append((entity_name, similarity))

                    # Sort by similarity and take top results
                    scored_entities.sort(key=lambda x: x[1], reverse=True)
                    for entity_name, _ in scored_entities[:limit]:
                        if entity_name not in entities:
                            entities.append(entity_name)
                            if len(entities) >= limit:
                                break
                except Exception:
                    pass

            # Get relationships for found entities with better traversal
            for entity in entities[:limit]:
                # Get direct relationships
                rel_query = """
                MATCH (e {name: $entity_name})-[r]->(target)
                WHERE target.name IS NOT NULL
                RETURN e.name as source, type(r) as rel_type, target.name as target
                LIMIT 15
                """

                try:
                    result = session.run(rel_query, entity_name=entity)
                    for record in result:
                        source = record.get("source")
                        rel_type = record.get("rel_type")
                        target = record.get("target")
                        if source and rel_type and target:
                            rel_str = f"{source} -[{rel_type}]-> {target}"
                            relationships.add(rel_str)
                except Exception:
                    continue

                # Also get incoming relationships (reverse)
                reverse_rel_query = """
                MATCH (source)-[r]->(e {name: $entity_name})
                WHERE source.name IS NOT NULL
                RETURN source.name as source, type(r) as rel_type, e.name as target
                LIMIT 15
                """

                try:
                    result = session.run(reverse_rel_query, entity_name=entity)
                    for record in result:
                        source = record.get("source")
                        rel_type = record.get("rel_type")
                        target = record.get("target")
                        if source and rel_type and target:
                            rel_str = f"{source} -[{rel_type}]-> {target}"
                            relationships.add(rel_str)
                except Exception:
                    continue

    except Exception as e:
        # If all strategies fail, return what we have
        pass

    return {
        'entities': entities[:limit],
        'relationships': list(relationships)[:limit]
    }


def query_knowledge_graph(
    query: str,
    graph_store: Neo4jPropertyGraphStore,
    llm: BedrockConverse,
    limit: int = 20,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Query the knowledge graph and generate an answer using the LLM.

    Retrieves context from the graph and uses an LLM to synthesize a response.

    Args:
        query: User query string
        graph_store: Neo4j graph store instance
        llm: Bedrock LLM instance for synthesis
        limit: Maximum number of entities to retrieve
        chat_history: Optional chat history for multi-turn conversations

    Returns:
        Generated answer string
    """
    try:
        # Retrieve context from graph
        context_data = retrieve_context_from_graph(query, graph_store, limit)

        entities = context_data.get('entities', [])
        relationships = context_data.get('relationships', [])

        # Build context string
        context_str = "Knowledge Graph Context:\n"
        if entities:
            context_str += f"Relevant Entities: {', '.join(entities[:10])}\n"
        if relationships:
            context_str += "Relationships:\n"
            for rel in relationships[:10]:
                context_str += f"  {rel}\n"

        # Build the prompt
        system_prompt = """You are a knowledge graph expert. Answer questions based on the provided knowledge graph context.
If the information is not available in the knowledge base, clearly state that.
Provide accurate, concise answers grounded in the graph data."""

        # Format conversation history if provided
        messages = []
        if chat_history:
            for msg in chat_history[-4:]:  # Keep last 4 messages
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        # Add current query
        user_message = f"{context_str}\n\nQuestion: {query}"

        # Call LLM
        response = llm.complete(user_message)

        return response.text if hasattr(response, 'text') else str(response)

    except Exception as e:
        return f"Error querying knowledge graph: {str(e)}"
