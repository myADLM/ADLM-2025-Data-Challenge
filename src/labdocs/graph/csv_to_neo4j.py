"""Load entities and relationships from CSV files into Neo4j."""
import argparse
import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase


class Neo4jCSVLoader:
    """
    Load CSV data (entities and relationships) into Neo4j graph database.
    """

    def __init__(self, uri: str, username: str, password: str, database: str = "neo4j"):
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        """Close Neo4j driver."""
        self.driver.close()

    def clear_graph(self):
        """Clear all nodes and relationships from graph."""
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("✓ Cleared existing graph")

    def load_entities(self, entities_csv: str) -> int:
        """
        Load entities from CSV into Neo4j.
        Creates nodes with canonical IDs and properties.
        """
        df = pd.read_csv(entities_csv)
        # Strip whitespace from column names
        df.columns = df.columns.str.strip()
        created_count = 0

        with self.driver.session(database=self.database) as session:
            for _, row in df.iterrows():
                entity_id = str(row["entity_id"]).strip()
                entity_type = str(row["entity_type"]).strip()
                title = str(row["title"]).strip() if pd.notna(row["title"]) else ""
                description = str(row["description"]).strip() if pd.notna(row["description"]) and row["description"] != "" else ""
                source_doc = str(row["source_document"]).strip()

                # Create node with label matching entity type
                query = """
                CREATE (n:{label} {{
                    canonical_id: $id,
                    title: $title,
                    description: $description,
                    source_document: $source_doc
                }})
                RETURN n
                """.format(label=entity_type)

                session.run(
                    query,
                    id=entity_id,
                    title=title,
                    description=description,
                    source_doc=source_doc
                )
                created_count += 1

        print(f"✓ Created {created_count} entity nodes")
        return created_count

    def load_relationships(self, relationships_csv: str) -> int:
        """
        Load relationships from CSV into Neo4j.
        Creates relationships between existing nodes.
        """
        df = pd.read_csv(relationships_csv)
        # Strip whitespace from column names
        df.columns = df.columns.str.strip()
        created_count = 0
        failed_count = 0

        with self.driver.session(database=self.database) as session:
            for _, row in df.iterrows():
                source_id = str(row["source_id"]).strip()
                target_id = str(row["target_id"]).strip()
                rel_type = str(row["relationship_type"]).strip()
                source_text = str(row["source_text"]).strip() if pd.notna(row["source_text"]) and row["source_text"] != "" else ""
                source_doc = str(row["source_document"]).strip()

                # Create relationship between nodes
                query = """
                MATCH (source {{canonical_id: $source_id}})
                MATCH (target {{canonical_id: $target_id}})
                CREATE (source)-[r:{rel_type} {{
                    source_text: $source_text,
                    source_document: $source_doc
                }}]->(target)
                RETURN r
                """.format(rel_type=rel_type)

                try:
                    result = session.run(
                        query,
                        source_id=source_id,
                        target_id=target_id,
                        source_text=source_text,
                        source_doc=source_doc
                    )
                    # Check if relationship was created
                    if result.consume().counters.relationships_created > 0:
                        created_count += 1
                except Exception as e:
                    failed_count += 1
                    print(f"  Warning: Could not create relationship {source_id} -> {target_id}: {e}")

        print(f"✓ Created {created_count} relationships ({failed_count} failed)")
        return created_count

    def get_graph_stats(self) -> dict:
        """Get statistics about the loaded graph."""
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

    parser = argparse.ArgumentParser(description="Load CSV data into Neo4j")
    parser.add_argument("--entities-csv", default="graphdb/entities.csv", help="Path to entities CSV")
    parser.add_argument("--relationships-csv", default="graphdb/relationships.csv", help="Path to relationships CSV")
    parser.add_argument("--neo4j-uri", default=None, help="Neo4j connection URI")
    parser.add_argument("--neo4j-user", default=None, help="Neo4j username")
    parser.add_argument("--neo4j-password", default=None, help="Neo4j password")
    parser.add_argument("--clear", action="store_true", help="Clear existing graph before loading")

    args = parser.parse_args()

    # Get Neo4j credentials from args or env
    neo4j_uri = args.neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = args.neo4j_user or os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = args.neo4j_password or os.getenv("NEO4J_PASSWORD", "your_neo4j_password")

    print(f"Connecting to Neo4j: {neo4j_uri}")

    loader = Neo4jCSVLoader(neo4j_uri, neo4j_user, neo4j_password)

    try:
        # Check files exist
        if not Path(args.entities_csv).exists():
            print(f"✗ Entities CSV not found: {args.entities_csv}")
            return
        if not Path(args.relationships_csv).exists():
            print(f"✗ Relationships CSV not found: {args.relationships_csv}")
            return

        if args.clear:
            loader.clear_graph()

        print(f"\nLoading entities from {args.entities_csv}...")
        entity_count = loader.load_entities(args.entities_csv)

        print(f"\nLoading relationships from {args.relationships_csv}...")
        rel_count = loader.load_relationships(args.relationships_csv)

        print("\n" + "=" * 60)
        print("GRAPH STATISTICS")
        print("=" * 60)
        stats = loader.get_graph_stats()
        print(f"Total nodes: {stats['total_nodes']}")
        print(f"Total relationships: {stats['total_relationships']}")
        print(f"Entity types: {', '.join(stats['entity_types'])}")
        print("=" * 60)

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        loader.close()


if __name__ == "__main__":
    main()
