"""Schema validation for extracted entities and relationships."""
from typing import Dict, Tuple
from .config import SchemaConfig


class SchemaValidator:
    """
    Validate that extracted entities and relationships conform to ontology schema.
    """

    def __init__(self, schema_config: SchemaConfig):
        self.schema_config = schema_config
        self.entity_types = set(schema_config.entity_types)
        self.relationship_types = set(schema_config.relationship_types)

    def validate_extraction(self, extraction_result: Dict) -> Tuple[Dict, Dict]:
        """
        Validate extracted entities and relationships.
        Returns (validated_result, validation_stats).
        """
        graph_data = extraction_result.get("@graph", [])

        validated_entities = []
        validated_relationships = []
        validation_stats = {
            "total_entities": len(graph_data),
            "valid_entities": 0,
            "invalid_entities": 0,
            "total_relationships": 0,
            "valid_relationships": 0,
            "invalid_relationships": 0,
            "errors": []
        }

        # Collect all entity IDs for relationship validation
        entity_ids = set()

        # Validate entities
        for entity in graph_data:
            entity_id = entity.get("@id")
            entity_type = entity.get("@type")
            entity_ids.add(entity_id)

            # Check entity type
            if entity_type not in self.entity_types:
                validation_stats["invalid_entities"] += 1
                validation_stats["errors"].append({
                    "type": "invalid_entity_type",
                    "entity_id": entity_id,
                    "provided_type": entity_type,
                    "valid_types": list(self.entity_types)
                })
                continue

            validated_entities.append(entity)
            validation_stats["valid_entities"] += 1

        # Validate relationships
        for entity in graph_data:
            entity_id = entity.get("@id")
            relations = entity.get("relations", [])

            for rel in relations:
                validation_stats["total_relationships"] += 1
                rel_type = rel.get("predicate")
                target_id = rel.get("object")
                source_text = rel.get("source_text")

                errors = []

                # Check relationship type
                if rel_type not in self.relationship_types:
                    errors.append(f"invalid_relationship_type: {rel_type}")

                # Check target entity exists
                if target_id not in entity_ids:
                    errors.append(f"target_entity_not_found: {target_id}")

                # Check source text exists
                if not source_text:
                    errors.append("missing_source_text")

                if errors:
                    validation_stats["invalid_relationships"] += 1
                    validation_stats["errors"].append({
                        "type": "invalid_relationship",
                        "source_id": entity_id,
                        "target_id": target_id,
                        "predicate": rel_type,
                        "errors": errors
                    })
                else:
                    validated_relationships.append({
                        "source_id": entity_id,
                        "target_id": target_id,
                        "type": rel_type,
                        "source_text": source_text
                    })
                    validation_stats["valid_relationships"] += 1

        return {
            "entities": validated_entities,
            "relationships": validated_relationships
        }, validation_stats

    def validate_entity(self, entity_type: str) -> bool:
        """Check if entity type is in schema."""
        return entity_type in self.entity_types

    def validate_relationship(self, rel_type: str) -> bool:
        """Check if relationship type is in schema."""
        return rel_type in self.relationship_types

    def validate_entity_relationship_pair(
        self,
        source_entity_type: str,
        rel_type: str,
        target_entity_type: str
    ) -> bool:
        """
        Check if relationship is valid between source and target entity types.
        Uses kg_validation_schema which maps entity types to allowed relationships.
        """
        if source_entity_type not in self.entity_types:
            return False

        if rel_type not in self.relationship_types:
            return False

        if target_entity_type not in self.entity_types:
            return False

        # Check if source entity type can have this relationship
        allowed_rels = self.schema_config.kg_validation_schema.get(source_entity_type, [])
        return rel_type in allowed_rels
