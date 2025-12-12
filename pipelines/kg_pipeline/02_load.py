"""
Load extracted entities and relationships into Neo4j graph database.
Generates embeddings and stores them in a vector store for PropertyGraphIndex.
"""
import argparse
import json
import os
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Set, Any

from dotenv import load_dotenv
from llama_index.core.graph_stores.types import EntityNode
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core.schema import TextNode
from llama_index.core import StorageContext
from neo4j.exceptions import ServiceUnavailable, AuthError, TransientError, ClientError

from logger import setup_logger


# Initialize logger
logger = setup_logger("kg_pipeline.load")


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
    # Always use 'neo4j' database (Community Edition doesn't support multiple databases)
    database = "neo4j"
    
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
        logger.info(f"Connected to Neo4j (uri: {uri}, database: {database})")
        return graph_store
    except (ServiceUnavailable, AuthError, ClientError) as e:
        logger.error(f"Neo4j connection error: {e}")
        raise


def get_bedrock_embedding():
    """
    Initialize Bedrock embedding model with credentials from environment variables.

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
            model_name="amazon.titan-embed-text-v1",
            region_name=aws_region,
            profile_name=aws_profile,
        )
        logger.info(f"Initialized Bedrock embedding model (profile: {aws_profile}, region: {aws_region})")
        return embed_model
    except Exception as e:
        logger.error(f"Failed to initialize Bedrock embedding model: {e}")
        raise
    

def get_or_create_vector_store(vector_dir: Path = None) -> tuple[SimpleVectorStore, Path]:
    """Load or create vector store for embeddings."""
    if vector_dir is None:
        vector_dir = Path("./graphdb_vectorstore")
    vector_dir.mkdir(parents=True, exist_ok=True)

    try:
        storage_context = StorageContext.from_defaults(persist_dir=str(vector_dir))
        vector_store = storage_context.vector_store
        logger.debug(f"Loaded vector store from {vector_dir}")
    except Exception:
        vector_store = SimpleVectorStore(stores_text=True)
        logger.debug(f"Created new vector store")

    return vector_store, vector_dir


def string_similarity(a: str, b: str) -> float:
    """
    Calculate similarity ratio between two strings.
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        Similarity ratio between 0.0 and 1.0
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_or_create_entity(
    name: str,
    entity_type: str,
    graph_store: Neo4jPropertyGraphStore,
    embed_model: BedrockEmbedding,
    similarity_threshold: float = 0.85
) -> EntityNode:
    """
    Find existing entity by exact match or similarity, or create new one with embedding.
    
    Args:
        name: Entity name to find or create
        entity_type: Type/label of the entity
        graph_store: Neo4j graph store instance
        embed_model: Embedding model for generating embeddings (required)
        similarity_threshold: Minimum similarity ratio for merging (default: 0.85)
        
    Returns:
        EntityNode with canonical name (may be merged with existing entity)
        
    Raises:
        TransientError: If Neo4j query fails
    """
    try:
        with graph_store._driver.session() as session:
            # Check for exact match first
            result = session.run(
                f"MATCH (n:{entity_type} {{name: $name}}) RETURN n, n.embedding as has_embedding LIMIT 1",
                name=name,
            )
            record = result.single()
            if record:
                # Entity exists - ensure it has an embedding
                if not record["has_embedding"]:
                    # Generate and store embedding for existing entity
                    text_content = f"{name}. Type: {entity_type}"
                    embedding = embed_model.get_text_embedding(text_content)
                    session.run(
                        f"""
                        MATCH (n:{entity_type} {{name: $name}})
                        SET n.embedding = $embedding
                        """,
                        name=name,
                        embedding=embedding
                    )
                    logger.debug(f"Added embedding to existing entity: {name} ({entity_type})")
                return EntityNode(name=name, label=entity_type)

            # Check for similar entities
            result = session.run(f"MATCH (n:{entity_type}) RETURN n.name as entity_name LIMIT 20")
            for record in result:
                existing_name = record["entity_name"]
                if string_similarity(name, existing_name) > similarity_threshold:
                    logger.debug(f"Merged '{name}' with '{existing_name}'")
                    # Ensure the merged entity has an embedding
                    merge_result = session.run(
                        f"MATCH (n:{entity_type} {{name: $name}}) RETURN n.embedding as has_embedding LIMIT 1",
                        name=existing_name
                    )
                    merge_record = merge_result.single()
                    if merge_record and not merge_record["has_embedding"]:
                        text_content = f"{existing_name}. Type: {entity_type}"
                        embedding = embed_model.get_text_embedding(text_content)
                        session.run(
                            f"""
                            MATCH (n:{entity_type} {{name: $name}})
                            SET n.embedding = $embedding
                            """,
                            name=existing_name,
                            embedding=embedding
                        )
                        logger.debug(f"Added embedding to merged entity: {existing_name} ({entity_type})")
                    return EntityNode(name=existing_name, label=entity_type)

        # Create new entity with embedding (always required now)
        # Generate embedding for new entity
        text_content = f"{name}. Type: {entity_type}"
        embedding = embed_model.get_text_embedding(text_content)
        
        # Store embedding in Neo4j
        with graph_store._driver.session() as session:
            session.run(
                f"""
                MERGE (n:{entity_type} {{name: $name}})
                SET n.title = $name, n.embedding = $embedding
                """,
                name=name,
                embedding=embedding
            )
        logger.debug(f"Created entity with embedding: {name} ({entity_type})")
        
        return EntityNode(name=name, label=entity_type)
    except TransientError as e:
        logger.error(f"Neo4j query error finding entity '{name}': {e}")
        raise


# DEPRECATED: Using Neo4j-based tracking now
def get_load_status_file(extraction_dir: Path) -> Path:
    """
    Get path to the load status file.
    
    Args:
        extraction_dir: Directory containing extraction files
        
    Returns:
        Path to status file
    """
    return extraction_dir / ".load_status.json"


def load_processed_documents(extraction_dir: Path) -> Dict[str, Dict[str, Any]]:
    """
    Load tracking information for already processed documents.
    
    Args:
        extraction_dir: Directory containing extraction files
        
    Returns:
        Dictionary mapping document_name to processing info
    """
    status_file = get_load_status_file(extraction_dir)
    if not status_file.exists():
        return {}
    
    try:
        with open(status_file, "r") as f:
            data = json.load(f)
            return data.get("processed_documents", {})
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Could not read load status file: {e}")
        return {}


def save_processed_document(
    extraction_dir: Path,
    document_name: str,
    json_file: Path,
    entity_count: int,
    relationship_count: int
) -> None:
    """
    Mark a document as successfully processed.
    
    Args:
        extraction_dir: Directory containing extraction files
        document_name: Name of the document
        json_file: Path to the JSON file
        entity_count: Number of entities loaded
        relationship_count: Number of relationships loaded
    """
    status_file = get_load_status_file(extraction_dir)
    
    # Load existing status
    if status_file.exists():
        try:
            with open(status_file, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            data = {}
    else:
        data = {}
    
    # Initialize structure if needed
    if "processed_documents" not in data:
        data["processed_documents"] = {}
    
    # Update status
    data["last_processed"] = datetime.now().isoformat()
    try:
        # Try to get relative path
        rel_path = json_file.relative_to(extraction_dir)
        file_path = str(rel_path)
    except ValueError:
        # If not relative, just use filename
        file_path = json_file.name
    
    data["processed_documents"][document_name] = {
        "file_path": file_path,
        "file_name": json_file.name,
        "entity_count": entity_count,
        "relationship_count": relationship_count,
        "loaded_at": datetime.now().isoformat(),
        "file_mtime": json_file.stat().st_mtime
    }
    
    # Save status
    try:
        with open(status_file, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        logger.warning(f"Could not save load status: {e}")


def is_document_processed(
    graph_store: Neo4jPropertyGraphStore,
    document_name: str,
    json_file: Path
) -> bool:
    """
    Check if a document has already been processed by querying Neo4j.
    
    Args:
        graph_store: Neo4j graph store connection
        document_name: Name of the document
        json_file: Path to the JSON file
        
    Returns:
        True if document was already processed, False otherwise
    """
    try:
        with graph_store._driver.session() as session:
            result = session.run(
                """
                MATCH (doc:ProcessedDocument {document_name: $document_name})
                RETURN doc.file_mtime as stored_mtime, doc.processed_at as processed_at
                """,
                document_name=document_name
            )
            
            record = result.single()
            if not record:
                return False
            
            # Check if file was modified since last processing
            stored_mtime = record["stored_mtime"]
            current_mtime = json_file.stat().st_mtime
            
            if current_mtime > stored_mtime:
                logger.debug(f"Document '{document_name}' was modified, will reload")
                return False
            
            return True
            
    except Exception as e:
        logger.warning(f"Error checking document status in Neo4j: {e}")
        return False


def mark_document_processed(
    graph_store: Neo4jPropertyGraphStore,
    document_name: str,
    json_file: Path
) -> None:
    """
    Mark a document as processed in Neo4j.
    
    Args:
        graph_store: Neo4j graph store connection
        document_name: Name of the document
        json_file: Path to the JSON file
    """
    try:
        with graph_store._driver.session() as session:
            session.run(
                """
                MERGE (doc:ProcessedDocument {document_name: $document_name})
                SET doc.file_path = $file_path,
                    doc.file_mtime = $file_mtime,
                    doc.processed_at = datetime()
                """,
                document_name=document_name,
                file_path=str(json_file),
                file_mtime=json_file.stat().st_mtime
            )
    except Exception as e:
        logger.warning(f"Could not mark document as processed: {e}")


def load_extraction(
    json_file: Path,
    graph_store: Neo4jPropertyGraphStore,
    embed_model: BedrockEmbedding,
    vector_store: SimpleVectorStore = None,
) -> None:
    """
    Load extraction file into Neo4j and generate embeddings for vector store.

    Args:
        json_file: Path to JSON extraction file
        graph_store: Neo4j graph store instance
        embed_model: Bedrock embedding model
        vector_store: Optional SimpleVectorStore for embeddings
    """
    try:
        with open(json_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Extraction file not found: {json_file}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {json_file}: {e}")
        raise

    document_name = data.get("document_name") or data.get("source_document", "unknown")
    entities = data["entities"]
    relationships = data["relationships"]
    total_relations = sum(len(entity.get("relations", [])) for entity in entities) + len(relationships)

    logger.info(f"Loading: {document_name}")
    logger.info(f"  Entities: {len(entities)}, Relationships: {total_relations}")

    all_relationships = []
    vector_nodes = []

    try:
        for entity_data in entities:
            entity_id = entity_data.get("@id") or entity_data.get("name") or entity_data.get("title", "unknown")
            entity_type = entity_data.get("type") or entity_data.get("@type", "Entity")
            entity_title = entity_data.get("title") or entity_data.get("name") or entity_id

            canonical_entity = find_or_create_entity(entity_id, entity_type, graph_store, embed_model)
            graph_store.upsert_nodes([canonical_entity])

            # Generate embedding and add to vector store
            if vector_store:
                entity_desc = entity_data.get("description", "")
                text = f"{entity_title}\n{entity_type}\n{entity_desc}"
                try:
                    embedding = embed_model.get_text_embedding(text)
                    node = TextNode(
                        text=text,
                        metadata={
                            "entity_id": entity_id,
                            "entity_type": entity_type,
                            "document": document_name,
                        },
                        embedding=embedding,
                    )
                    vector_nodes.append(node)
                except Exception as e:
                    logger.warning(f"Failed to embed {entity_id}: {e}")

            entity_relations = entity_data.get("relations", [])
            for rel in entity_relations:
                all_relationships.append({
                    "source": entity_id,
                    "target": rel.get("object", "unknown"),
                    "relation_type": rel.get("predicate", "RELATED_TO"),
                    "source_text": rel.get("source_text", "")
                })

        # Also process any top-level relationships (for backward compatibility)
        for rel_data in relationships:
            source_name = rel_data.get("source", "unknown")
            target_name = rel_data.get("target", "unknown") 
            rel_type = rel_data.get("relation_type", "RELATED_TO")
            all_relationships.append({
                "source": source_name,
                "target": target_name,
                "relation_type": rel_type,
                "source_text": rel_data.get("source_text", "")
            })

        # First pass: Create all relationships that have existing entities
        # Also collect missing entities that need to be created
        created_count = 0
        failed_count = 0
        failed_rels = []
        missing_entities = {}  # entity_name -> rel_type_hint

        with graph_store._driver.session() as session:
            for rel_data in all_relationships:
                source_name = rel_data["source"]
                target_name = rel_data["target"]
                rel_type = rel_data["relation_type"]

                try:
                    # Try to match by any identifier property (name, id, or any indexed property)
                    result = session.run(
                        f"""
                        MATCH (source)
                        WHERE source.name = $source_name OR id(source) = $source_name OR source.id = $source_name
                        MATCH (target)
                        WHERE target.name = $target_name OR id(target) = $target_name OR target.id = $target_name
                        MERGE (source)-[r:{rel_type}]->(target)
                        RETURN count(r) as created
                        """,
                        source_name=source_name,
                        target_name=target_name,
                    )
                    record = result.single()
                    if record and record["created"] > 0:
                        created_count += 1
                    else:
                        # Check if source exists
                        source_exists = session.run(
                            "MATCH (n) WHERE n.name = $name OR n.id = $name RETURN COUNT(n) > 0 as exists",
                            name=source_name
                        ).single()

                        # Check if target exists
                        target_exists = session.run(
                            "MATCH (n) WHERE n.name = $name OR n.id = $name RETURN COUNT(n) > 0 as exists",
                            name=target_name
                        ).single()

                        if not target_exists["exists"]:
                            # Mark target as missing - infer type from entity ID pattern
                            entity_type = "Unknown"
                            if "_" in target_name:
                                entity_type = target_name.split("_")[0]
                            missing_entities[target_name] = entity_type

                        if not source_exists["exists"] or not target_exists["exists"]:
                            failed_count += 1
                            failed_rels.append(f"{source_name} -[{rel_type}]-> {target_name}")
                            logger.debug(f"Failed to create relationship: {source_name} -[{rel_type}]-> {target_name} (one entity missing)")

                except Exception as e:
                    failed_count += 1
                    failed_rels.append(f"{source_name} -[{rel_type}]-> {target_name}")
                    logger.debug(f"Error creating relationship {source_name} -[{rel_type}]-> {target_name}: {e}")

        # Second pass: Create missing entities if any were found
        if missing_entities:
            logger.debug(f"Creating {len(missing_entities)} missing entities")
            for entity_name, entity_type in missing_entities.items():
                try:
                    with graph_store._driver.session() as session:
                        session.run(
                            f"MERGE (n:{entity_type} {{name: $name}})",
                            name=entity_name
                        )
                        logger.debug(f"Created missing entity: {entity_name} ({entity_type})")
                except Exception as e:
                    logger.warning(f"Failed to create missing entity {entity_name}: {e}")

        # Third pass: Retry failed relationships if we created missing entities
        if missing_entities and failed_rels:
            logger.debug(f"Retrying {len(failed_rels)} relationships after creating missing entities")
            with graph_store._driver.session() as session:
                for rel_str in failed_rels:
                    # Parse the relationship string
                    parts = rel_str.split(" -[")
                    if len(parts) == 2:
                        source_name = parts[0]
                        rest = parts[1].split("]-> ")
                        if len(rest) == 2:
                            rel_type = rest[0]
                            target_name = rest[1]

                            try:
                                result = session.run(
                                    f"""
                                    MATCH (source)
                                    WHERE source.name = $source_name
                                    MATCH (target)
                                    WHERE target.name = $target_name
                                    MERGE (source)-[r:{rel_type}]->(target)
                                    RETURN count(r) as created
                                    """,
                                    source_name=source_name,
                                    target_name=target_name,
                                )
                                record = result.single()
                                if record and record["created"] > 0:
                                    created_count += 1
                                    failed_count -= 1
                            except Exception:
                                pass

        if created_count > 0:
            logger.info(f"  Created {created_count} relationships")
        if failed_count > 0:
            logger.warning(f"  Failed to create {failed_count} relationships (check data integrity)")

        # Add vector nodes to vector store
        if vector_store and vector_nodes:
            try:
                vector_store.add(vector_nodes)
                logger.debug(f"Added {len(vector_nodes)} embeddings to vector store")
            except Exception as e:
                logger.warning(f"Failed to add embeddings to vector store: {e}")

        mark_document_processed(graph_store, document_name, json_file)
        logger.info(f"  [OK] Loaded {document_name} ({len(vector_nodes)} embeddings)")
    except TransientError as e:
        logger.error(f"Neo4j error loading {document_name}: {e}")
        raise


def main() -> None:
    """Main loading function."""
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Load extracted entities and relationships into Neo4j graph database"
    )
    parser.add_argument(
        "--extraction-dir",
        required=True,
        help="Directory containing JSON extraction files from 01_extract.py"
    )
    parser.add_argument(
        "--clear-database",
        action="store_true",
        help="Clear existing database before loading (recommended when adding embeddings)"
    )

    args = parser.parse_args()

    extraction_path = Path(args.extraction_dir)

    if not extraction_path.exists():
        logger.warning("No extractions found. Run 01_extract.py first.")
        return

    # Initialize graph store
    try:
        logger.info("Initializing Neo4j graph store...")
        graph_store = get_graph_store()
        logger.info("[OK] Graph store connected")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return
    except (ServiceUnavailable, AuthError) as e:
        logger.error(f"Neo4j connection error: {e}")
        return

    # Initialize embedding model
    try:
        logger.info("Initializing Bedrock embedding model...")
        embed_model = get_bedrock_embedding()
        logger.info("[OK] Embedding model initialized")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return
    except Exception as e:
        logger.error(f"Embedding model initialization error: {e}")
        return

    # Initialize vector store
    try:
        logger.info("Initializing vector store...")
        vector_store, vector_dir = get_or_create_vector_store()
        logger.info(f"[OK] Vector store initialized at {vector_dir}")
    except Exception as e:
        logger.error(f"Vector store initialization error: {e}")
        return

    # Clear database if requested
    if args.clear_database:
        logger.info("Clearing existing database...")
        try:
            with graph_store._driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
            logger.info("✅ Database cleared")
            
            # Also clear the processing status from Neo4j
            with graph_store._driver.session() as session:
                result = session.run("MATCH (doc:ProcessedDocument) DELETE doc")
                logger.info("✅ Processing status cleared from Neo4j")
        except Exception as e:
            logger.error(f"Failed to clear database: {e}")
            return

    # Find extraction files (exclude status files)
    logger.info("")
    logger.info("=" * 70)
    logger.info("Loading Knowledge Graph from Extractions")
    logger.info("=" * 70)
    logger.info(f"Extraction directory: {extraction_path}")

    extraction_files = [
        f for f in sorted(extraction_path.glob("*.json"))
        if not f.name.startswith(".")  # Exclude hidden files like .load_status.json
    ]
    logger.info(f"Found {len(extraction_files)} extraction files")

    if not extraction_files:
        logger.warning("No extraction files found.")
        return

    # Filter out already processed documents using Neo4j
    unprocessed_files = []
    skipped_count = 0

    logger.info("Checking processing status...")
    for json_file in extraction_files:
        try:
            # Read document name from JSON file
            with open(json_file, "r") as f:
                data = json.load(f)
                document_name = data.get("document_name") or data.get("source_document", json_file.stem)

            if is_document_processed(graph_store, document_name, json_file):
                logger.debug(f"Skipping already processed: {document_name}")
                skipped_count += 1
            else:
                unprocessed_files.append((json_file, document_name))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not check status for {json_file.name}: {e}, will attempt to load")
            unprocessed_files.append((json_file, json_file.stem))

    logger.info("")
    logger.info(f"Already processed: {skipped_count}")
    logger.info(f"To process: {len(unprocessed_files)}")
    
    if not unprocessed_files:
        logger.info("No new documents to load")
        return

    # Load each extraction
    loaded_count = 0
    failed_count = 0
    total_files = len(unprocessed_files)

    for file_idx, (json_file, document_name) in enumerate(unprocessed_files):
        try:
            # Read data again to get entity/relationship counts
            with open(json_file, "r") as f:
                data = json.load(f)

            entity_count = len(data.get("entities", []))
            relationship_count = len(data.get("relationships", []))

            # Log progress
            logger.info(f"Processing [{file_idx + 1}/{total_files}]: {document_name}")

            # Load the extraction
            load_extraction(json_file, graph_store, embed_model, vector_store)

            # Mark as processed
            save_processed_document(
                extraction_path,
                document_name,
                json_file,
                entity_count,
                relationship_count
            )

            logger.info(f"  [OK] Loaded {entity_count} entities, {relationship_count} relationships")
            loaded_count += 1
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"  [FAIL] Error loading {json_file.name}: {e}")
            failed_count += 1
        except TransientError as e:
            logger.error(f"  [FAIL] Neo4j error loading {json_file.name}: {e}")
            failed_count += 1
        except Exception as e:
            logger.error(f"  [FAIL] Unexpected error loading {json_file.name}: {e}", exc_info=True)
            failed_count += 1

    # Persist vector store
    try:
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        storage_context.persist(persist_dir=str(vector_dir))
        logger.info(f"Vector store persisted to {vector_dir}")
    except Exception as e:
        logger.error(f"Failed to persist vector store: {e}")

    # Print statistics
    logger.info("=" * 70)
    logger.info("Loading Complete!")
    logger.info(f"Loaded: {loaded_count}/{total_files} documents")
    logger.info(f"Skipped: {skipped_count}")
    logger.info(f"Failed: {failed_count}")

    try:
        with graph_store._driver.session() as session:
            node_result = session.run("MATCH (n) WHERE n.name IS NOT NULL RETURN count(n) as count").single()
            rel_result = session.run("MATCH ()-[r]-() RETURN count(r) as count").single()

            node_count = node_result[0] if node_result else 0
            rel_count = rel_result[0] if rel_result else 0

        logger.info("")
        logger.info("Graph Statistics:")
        logger.info(f"  Total nodes: {node_count}")
        logger.info(f"  Total relationships: {rel_count}")
        logger.info(f"Vector store location: {vector_dir}")
    except TransientError as e:
        logger.error(f"Failed to retrieve graph statistics: {e}")


if __name__ == "__main__":
    main()
