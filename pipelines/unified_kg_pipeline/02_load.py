#!/usr/bin/env python3
"""
Load extracted entities and relationships from JSON files into Neo4j.
Reads from unified ontology JSON extractions and loads into Neo4j graph.
Includes resume capability, error handling, and entity deduplication.

Usage:
    python 02_load.py --extraction-dir <extractions_directory>

Examples:
    python 02_load.py --extraction-dir graphdb_unified/extractions
    python 02_load.py --extraction-dir graphdb_unified/extractions --clear
"""
import argparse
import json
import logging
import os
import sys
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, Set, Any

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError, TransientError, ClientError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def string_similarity(a: str, b: str) -> float:
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def get_load_status_file(extraction_dir: Path) -> Path:
    """Get path to the load status file."""
    return extraction_dir / ".load_status.json"


def load_processed_documents(extraction_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Load tracking information for already processed documents."""
    status_file = get_load_status_file(extraction_dir)
    if not status_file.exists():
        return {}
    
    try:
        with open(status_file, 'r') as f:
            data = json.load(f)
            return data.get("processed_documents", {})
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Could not read load status file: {e}")
        return {}


def save_processed_document(extraction_dir: Path, document_name: str, json_file: Path, 
                          entity_count: int, rel_count: int) -> None:
    """Mark a document as successfully processed."""
    status_file = get_load_status_file(extraction_dir)
    
    # Load existing status
    if status_file.exists():
        try:
            with open(status_file, 'r') as f:
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
    data["processed_documents"][document_name] = {
        "file_name": json_file.name,
        "entity_count": entity_count,
        "relationship_count": rel_count,
        "loaded_at": datetime.now().isoformat(),
        "file_mtime": json_file.stat().st_mtime
    }
    
    # Save status
    try:
        with open(status_file, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        logger.warning(f"Could not save load status: {e}")


def is_document_processed(extraction_dir: Path, document_name: str, json_file: Path) -> bool:
    """Check if a document has already been processed."""
    processed = load_processed_documents(extraction_dir)
    
    if document_name not in processed:
        return False
    
    # Check if file was modified since last load
    file_info = processed[document_name]
    stored_mtime = file_info.get("file_mtime", 0)
    current_mtime = json_file.stat().st_mtime
    
    if current_mtime > stored_mtime:
        logger.debug(f"Document '{document_name}' was modified, will reload")
        return False
    
    return True


class Neo4jJSONLoader:
    def __init__(self, uri: str, username: str, password: str, database: str = "neo4j"):
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        try:
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
            logger.info(f"Connected to Neo4j (uri: {uri}, database: {database})")
        except (ServiceUnavailable, AuthError, ClientError) as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        if self.driver:
            self.driver.close()

    def clear_graph(self):
        """Clear all nodes and relationships from the graph."""
        try:
            with self.driver.session(database=self.database) as s:
                s.run("MATCH (n) DETACH DELETE n")
            logger.info("✓ Cleared existing graph")
        except Exception as e:
            logger.error(f"Failed to clear graph: {e}")
            raise

    def find_similar_entity(self, entity_id: str, entity_type: str, similarity_threshold: float = 0.85) -> str:
        """Find existing entity by similarity or return original ID."""
        try:
            with self.driver.session(database=self.database) as session:
                # Check for exact match first
                result = session.run(
                    f"MATCH (n:{entity_type} {{canonical_id: $id}}) RETURN n.canonical_id LIMIT 1",
                    id=entity_id
                )
                if result.single():
                    return entity_id

                # Check for similar entities
                result = session.run(
                    f"MATCH (n:{entity_type}) RETURN n.canonical_id as entity_id LIMIT 20"
                )
                for record in result:
                    existing_id = record["entity_id"]
                    if string_similarity(entity_id, existing_id) > similarity_threshold:
                        logger.debug(f"Merged '{entity_id}' with '{existing_id}'")
                        return existing_id

            return entity_id
        except Exception as e:
            logger.warning(f"Error finding similar entity for {entity_id}: {e}")
            return entity_id

    def load_json_extractions(self, extractions_dir: str) -> tuple:
        """Load JSON extractions with resume capability and error handling."""
        entity_count = 0
        rel_count = 0

        extractions_path = Path(extractions_dir)
        status_file = get_load_status_file(extractions_path)
        json_files = [f for f in sorted(extractions_path.glob("*.json")) if f != status_file]

        if not json_files:
            logger.warning(f"No JSON files found in {extractions_dir}")
            return 0, 0

        # Filter out already processed documents
        unprocessed_files = []
        skipped_count = 0
        
        for json_file in json_files:
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    # Use source_document path as document name, fallback to filename
                    source_doc = data.get("source_document", "")
                    if source_doc:
                        doc_name = Path(source_doc).stem
                    else:
                        doc_name = json_file.stem
                
                if is_document_processed(extractions_path, doc_name, json_file):
                    logger.debug(f"Skipping already processed: {doc_name}")
                    skipped_count += 1
                else:
                    unprocessed_files.append((json_file, doc_name, data))
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not check status for {json_file.name}: {e}, will attempt to load")
                unprocessed_files.append((json_file, json_file.stem, None))

        logger.info(f"Total files: {len(json_files)}")
        logger.info(f"Already processed: {skipped_count}")
        logger.info(f"To process: {len(unprocessed_files)}")

        if not unprocessed_files:
            logger.info("No new documents to process")
            return 0, 0

        with self.driver.session(database=self.database) as session:
            for json_file, doc_name, data in unprocessed_files:
                logger.info(f"Processing {json_file.name}...")

                try:
                    # Load data if not already loaded
                    if data is None:
                        with open(json_file) as f:
                            data = json.load(f)

                    # Load entities
                    entities = data.get("entities", [])
                    file_entity_count = 0
                    file_rel_count = 0

                    for entity in entities:
                        entity_id = entity.get("@id")
                        entity_type = entity.get("@type")
                        title = entity.get("title", "")
                        doc_type = entity.get("doc_type", "unknown")
                        source_doc = data.get("source_document", "")

                        if not entity_id or not entity_type:
                            continue

                        # Find similar entity for deduplication
                        canonical_id = self.find_similar_entity(entity_id, entity_type)

                        query = f"""
                        MERGE (n:{entity_type} {{canonical_id: $id}})
                        SET n.title = $title,
                            n.doc_type = $doc_type,
                            n.source_document = $source_doc
                        RETURN n
                        """

                        try:
                            session.run(
                                query,
                                id=canonical_id,
                                title=title,
                                doc_type=doc_type,
                                source_doc=source_doc
                            )
                            file_entity_count += 1
                            entity_count += 1
                        except Exception as e:
                            logger.warning(f"Could not create entity {entity_id}: {e}")

                    # Load relationships (nested in entities)
                    for entity in entities:
                        entity_id = entity.get("@id")
                        relations = entity.get("relations", [])

                        # Find canonical ID for source entity
                        entity_type = entity.get("@type")
                        canonical_source_id = self.find_similar_entity(entity_id, entity_type)

                        for relation in relations:
                            predicate = relation.get("predicate")
                            target_id = relation.get("object")
                            source_text = relation.get("source_text", "")

                            if not predicate or not target_id:
                                continue

                            query = f"""
                            MATCH (source {{canonical_id: $source_id}})
                            MATCH (target {{canonical_id: $target_id}})
                            MERGE (source)-[r:{predicate}]->(target)
                            SET r.source_text = $source_text,
                                r.source_document = $source_doc
                            RETURN r
                            """

                            try:
                                result = session.run(
                                    query,
                                    source_id=canonical_source_id,
                                    target_id=target_id,
                                    source_text=source_text,
                                    source_doc=source_doc
                                )
                                if result.consume().counters.relationships_created > 0:
                                    file_rel_count += 1
                                    rel_count += 1
                            except Exception as e:
                                logger.debug(f"Could not create relationship {predicate}: {e}")

                    logger.info(f"  ✓ {file_entity_count} entities, {file_rel_count} relationships")
                    
                    # Mark as processed
                    save_processed_document(extractions_path, doc_name, json_file, 
                                          file_entity_count, file_rel_count)

                except Exception as e:
                    logger.error(f"  ✗ Error processing {json_file.name}: {e}")

        return entity_count, rel_count

    def get_graph_stats(self) -> dict:
        with self.driver.session(database=self.database) as session:
            node_count = session.run("MATCH (n) RETURN COUNT(n) as count").single()["count"]
            rel_count = session.run("MATCH ()-[r]->() RETURN COUNT(r) as count").single()["count"]
            entity_types = list(session.run("""
                MATCH (n)
                RETURN DISTINCT labels(n) as label
                ORDER BY label
            """))

        stats = {
            "total_nodes": node_count,
            "total_relationships": rel_count,
            "entity_types": [record["label"][0] if record["label"] else "Unknown" for record in entity_types]
        }
        return stats


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Load extracted JSON entities and relationships into Neo4j"
    )
    parser.add_argument(
        "--extraction-dir",
        required=True,
        help="Directory containing extracted JSON files from 01_extract.py"
    )
    parser.add_argument(
        "--neo4j-uri",
        type=str,
        default=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        help="Neo4j connection URI"
    )
    parser.add_argument(
        "--neo4j-user",
        type=str,
        default=os.getenv('NEO4J_USER', 'neo4j'),
        help="Neo4j username"
    )
    parser.add_argument(
        "--neo4j-password",
        type=str,
        default=os.getenv('NEO4J_PASSWORD', 'neo4j'),
        help="Neo4j password"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing graph before loading"
    )

    args = parser.parse_args()

    extractions_dir = Path(args.extraction_dir)
    if not extractions_dir.exists():
        logger.error(f"Extraction directory not found: {extractions_dir}")
        return 1

    logger.info(f"Connecting to Neo4j: {args.neo4j_uri}")
    
    try:
        loader = Neo4jJSONLoader(args.neo4j_uri, args.neo4j_user, args.neo4j_password)
    except (ServiceUnavailable, AuthError, ClientError) as e:
        logger.error(f"Failed to connect to Neo4j: {e}")
        return 1

    try:
        if args.clear:
            loader.clear_graph()

        logger.info(f"Loading JSON extractions from {extractions_dir}...")
        entity_count, rel_count = loader.load_json_extractions(str(extractions_dir))

        logger.info("="*70)
        logger.info("LOADING SUMMARY")
        logger.info("="*70)
        logger.info(f"Total entities loaded: {entity_count}")
        logger.info(f"Total relationships loaded: {rel_count}")

        logger.info("="*70)
        logger.info("GRAPH STATISTICS")
        logger.info("="*70)
        stats = loader.get_graph_stats()
        logger.info(f"Total nodes: {stats['total_nodes']}")
        logger.info(f"Total relationships: {stats['total_relationships']}")
        logger.info(f"Entity types: {', '.join(sorted(stats['entity_types']))}")
        logger.info("="*70)

        return 0

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        loader.close()


if __name__ == "__main__":
    sys.exit(main())
