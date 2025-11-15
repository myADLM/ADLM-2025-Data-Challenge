"""Wrapper around Neo4jPGStore with document tracking and state management."""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

from llama_index.graph_stores.neo4j import Neo4jPGStore

from .config import Neo4jConfig

load_dotenv()


class GraphStoreWrapper:
    """
    Wrapper around Neo4jPGStore that manages:
    - Neo4j connection and node/relationship operations
    - Document processing status tracking
    - Deduplication statistics
    """

    def __init__(self, neo4j_config: Neo4jConfig, graphdb_dir: str = "./graphdb"):
        self.neo4j_config = neo4j_config
        self.graphdb_dir = Path(graphdb_dir)
        self.graphdb_dir.mkdir(exist_ok=True)

        self.status_file = self.graphdb_dir / "graphdb_status.json"
        self.store = Neo4jPGStore(
            url=neo4j_config.uri,
            username=neo4j_config.username,
            password=neo4j_config.password,
            database=neo4j_config.database
        )
        self.status = self._load_status()

    def _load_status(self) -> Dict:
        """Load processing status from disk."""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "last_processed": None,
            "graph_store": str(self.neo4j_config.uri),
            "processed_documents": {}
        }

    def _save_status(self):
        """Persist processing status to disk."""
        try:
            with open(self.status_file, 'w') as f:
                json.dump(self.status, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save status: {e}")

    def get_processed_documents(self) -> set:
        """Get set of documents already processed and stored in graphdb."""
        return set(self.status.get("processed_documents", {}).keys())

    def mark_document_processed(
        self,
        document_path: str,
        entity_count: int,
        relationship_count: int,
        extraction_model: str,
        dedup_stats: Dict = None
    ):
        """Mark a document as successfully processed."""
        self.status["last_processed"] = datetime.now().isoformat()
        self.status["processed_documents"][document_path] = {
            "vectordb_indexed": True,
            "graphdb_indexed": True,
            "entity_count": entity_count,
            "relationship_count": relationship_count,
            "extraction_model": extraction_model,
            "extraction_timestamp": datetime.now().isoformat(),
            "dedup_stats": dedup_stats or {}
        }
        self._save_status()

    def is_document_processed(self, document_path: str) -> bool:
        """Check if document is already in graphdb."""
        return document_path in self.get_processed_documents()

    def query(self, cypher_query: str, params: Dict = None) -> List:
        """
        Execute a Cypher query against Neo4j.
        Returns list of results.
        """
        try:
            result = self.store.query(cypher_query, params or {})
            return result if result else []
        except Exception as e:
            print(f"Query error: {e}")
            return []

    def upsert_node(self, node: Dict):
        """
        Insert or update a node in the graph.
        Node must have @id and @type fields.
        """
        try:
            node_id = node.get("@id")
            node_type = node.get("@type")

            if not node_id or not node_type:
                print(f"Warning: Node missing @id or @type: {node}")
                return

            # Use Neo4j's add_node method from PropertyGraphStore
            properties = {k: v for k, v in node.items() if k not in ["@id", "@type"]}
            self.store.add_node({
                "id": node_id,
                "type": node_type,
                **properties
            })
        except Exception as e:
            print(f"Error upserting node {node.get('@id')}: {e}")

    def upsert_nodes(self, nodes: List[Dict]):
        """Upsert multiple nodes."""
        for node in nodes:
            self.upsert_node(node)

    def upsert_relationship(self, relationship: Dict):
        """
        Insert or update a relationship in the graph.
        Relationship must have source_id, target_id, and type fields.
        """
        try:
            source_id = relationship.get("source_id")
            target_id = relationship.get("target_id")
            rel_type = relationship.get("type")

            if not source_id or not target_id or not rel_type:
                print(f"Warning: Relationship missing required fields: {relationship}")
                return

            properties = {
                k: v for k, v in relationship.items()
                if k not in ["source_id", "target_id", "type"]
            }

            # Use Neo4j's add_relationship method
            self.store.add_relationship({
                "source_id": source_id,
                "target_id": target_id,
                "type": rel_type,
                **properties
            })
        except Exception as e:
            print(f"Error upserting relationship {relationship}: {e}")

    def upsert_relationships(self, relationships: List[Dict]):
        """Upsert multiple relationships."""
        for rel in relationships:
            self.upsert_relationship(rel)

    def get_node_by_id(self, node_id: str) -> Optional[Dict]:
        """Retrieve a node by its ID."""
        try:
            result = self.query(
                "MATCH (n {canonical_id: $id}) RETURN n",
                {"id": node_id}
            )
            return result[0].get("n") if result else None
        except Exception:
            return None

    def get_all_nodes(self) -> List[Dict]:
        """Get all nodes from graph (for deduplication)."""
        try:
            result = self.query("MATCH (n) RETURN n LIMIT 10000")
            return [r.get("n") for r in result if r.get("n")]
        except Exception:
            return []

    def get_nodes_by_type(self, node_type: str) -> List[Dict]:
        """Get all nodes of a specific type."""
        try:
            result = self.query(
                f"MATCH (n:{node_type}) RETURN n",
            )
            return [r.get("n") for r in result if r.get("n")]
        except Exception:
            return []

    def close(self):
        """Close Neo4j connection."""
        try:
            self.store.close()
        except Exception:
            pass
