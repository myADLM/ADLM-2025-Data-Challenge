"""Configuration for Neo4j graph store and deduplication logic."""
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Neo4jConfig:
    """Neo4j connection configuration."""
    uri: str = "bolt://localhost:7687"
    username: str = "neo4j"
    password: str = "your_neo4j_password"
    database: str = "neo4j"


@dataclass
class DeduplicationConfig:
    """Entity and relationship deduplication configuration."""
    levenshtein_candidate_threshold: float = 0.7
    levenshtein_match_threshold: float = 0.8
    llm_confirmation_threshold: float = 0.85
    use_llm_reconciliation: bool = True


@dataclass
class SchemaConfig:
    """Ontology schema configuration loaded from schema file."""
    entity_types: List[str] = field(default_factory=list)
    relationship_types: List[str] = field(default_factory=list)
    kg_validation_schema: Dict = field(default_factory=dict)
    strict_schema: bool = False

    @classmethod
    def from_file(cls, schema_path: str = None):
        if schema_path is None:
            # Default path relative to prompts folder
            schema_path = Path(__file__).parent.parent / "prompts" / "ontology_schema.json"

        with open(schema_path, 'r') as f:
            schema_data = json.load(f)

        # Build validation schema: entity_type -> allowed relationships
        validation_schema = {}
        for entity_type in schema_data.get("entity_types", []):
            validation_schema[entity_type] = []

        for rel_type in schema_data.get("relationship_types", []):
            for entity_type in schema_data.get("entity_types", []):
                validation_schema[entity_type].append(rel_type)

        return cls(
            entity_types=schema_data.get("entity_types", []),
            relationship_types=schema_data.get("relationship_types", []),
            kg_validation_schema=validation_schema,
            strict_schema=False
        )


@dataclass
class GraphBuilderConfig:
    """Complete configuration for graph builder."""
    neo4j: Neo4jConfig = field(default_factory=Neo4jConfig)
    deduplication: DeduplicationConfig = field(default_factory=DeduplicationConfig)
    schema: SchemaConfig = field(default_factory=lambda: SchemaConfig.from_file())
    vectordb_dir: str = "./vectordb"
    graphdb_dir: str = "./graphdb"
