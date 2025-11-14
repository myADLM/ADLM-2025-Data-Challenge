"""
Visualize Neo4j knowledge graph with physics-based layout using PyVis.
Creates an interactive HTML visualization with node-link diagram.
"""
import os
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase
import pyvis.network as net

try:
    from pyvis.network import Network
except ImportError:
    print("Installing required dependencies...")
    os.system("uv pip install pyvis")
    from pyvis.network import Network


class KGVisualizer:
    """Visualize Neo4j knowledge graph."""

    def __init__(self, uri: str, username: str, password: str, database: str = "neo4j"):
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        """Close Neo4j driver."""
        self.driver.close()

    def get_graph_data(self):
        """
        Query Neo4j and return nodes and edges.
        """
        nodes = {}
        edges = []

        with self.driver.session(database=self.database) as session:
            # Get all nodes
            node_result = session.run("""
                MATCH (n)
                RETURN id(n) as node_id, labels(n) as labels,
                       n.canonical_id as canonical_id, n.title as title, n.description as description
            """)

            color_map = {
                'SOP': '#FF6B6B',
                'Assay': '#4ECDC4',
                'Analyte': '#45B7D1',
                'SpecimenType': '#FFA07A',
                'Instrument': '#98D8C8',
                'ReagentKit': '#F7DC6F',
                'ProcedureStep': '#BB8FCE',
                'ResultInterpretation': '#85C1E2',
                'CutoffValue': '#F8B88B',
                'Guideline': '#A3E4D7',
                'Limitation': '#F5A9A9',
                'ReferenceDocument': '#D7BDE2',
                'ControlType': '#ABEBC6',
                'PatientPopulation': '#F9E79F',
            }

            for record in node_result:
                node_id = record['node_id']
                labels = record['labels']
                canonical_id = record['canonical_id']
                title = record['title']
                node_type = labels[0] if labels else 'Unknown'

                nodes[node_id] = {
                    'id': canonical_id,
                    'label': title or canonical_id,
                    'type': node_type,
                    'color': color_map.get(node_type, '#95A5A6'),
                    'title': f"{node_type}: {title or canonical_id}\n{record['description'] or 'No description'}",
                }

            # Get all relationships
            rel_result = session.run("""
                MATCH (source)-[r]->(target)
                RETURN id(source) as source_id, id(target) as target_id, type(r) as rel_type, r.source_text as source_text
                LIMIT 5000
            """)

            for record in rel_result:
                source_id = record['source_id']
                target_id = record['target_id']
                rel_type = record['rel_type']
                source_text = record['source_text']

                if source_id in nodes and target_id in nodes:
                    edges.append({
                        'source': source_id,
                        'target': target_id,
                        'label': rel_type,
                        'title': source_text or rel_type,
                    })

        return nodes, edges

    def visualize(self, output_file: str = "kg_visualization.html", height: str = "1000px", width: str = "100%"):
        """
        Create interactive visualization with physics simulation.

        Args:
            output_file: Output HTML file path
            height: Height of visualization canvas
            width: Width of visualization canvas
        """
        print("Querying Neo4j graph...")
        nodes, edges = self.get_graph_data()

        print(f"Found {len(nodes)} nodes and {len(edges)} relationships")

        # Create network visualization
        print("Creating visualization with physics simulation...")
        g = Network(
            height=height,
            width=width,
            directed=True,
            notebook=False
        )

        # Configure physics simulation
        g.toggle_physics(True)
        g.show_buttons(filter_=['physics'])

        physics_config = {
            "physics": {
                "enabled": True,
                "barnesHut": {
                    "gravitationalConstant": -20000,
                    "centralGravity": 0.3,
                    "springLength": 200,
                    "springConstant": 0.04
                },
                "maxVelocity": 50,
                "minVelocity": 0.75,
                "solver": "barnesHut",
                "timeStep": 0.5,
                "stabilization": {
                    "iterations": 200
                }
            }
        }

        # Add nodes
        for node_id, node_data in nodes.items():
            g.add_node(
                node_id,
                label=node_data['label'],
                title=node_data['title'],
                color=node_data['color'],
                size=30,
                font={'size': 14}
            )

        # Add edges
        for edge in edges:
            g.add_edge(
                edge['source'],
                edge['target'],
                label=edge['label'],
                title=edge['title'],
                arrows='to'
            )

        # Apply physics configuration
        g.set_options(json.dumps(physics_config))

        # Save to file
        g.write_html(output_file)
        print(f"✓ Visualization saved to: {output_file}")
        print(f"  Open this file in a web browser to view the interactive graph")
        print(f"  Use mouse to drag/zoom, and physics simulation to arrange nodes")

        # Print file size
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"  File size: {file_size_mb:.2f} MB")

        return output_file


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Visualize Neo4j knowledge graph")
    parser.add_argument("--neo4j-uri", default=None, help="Neo4j connection URI")
    parser.add_argument("--neo4j-user", default=None, help="Neo4j username")
    parser.add_argument("--neo4j-password", default=None, help="Neo4j password")
    parser.add_argument("--output", default="kg_visualization.html", help="Output HTML file")
    parser.add_argument("--height", default="1000px", help="Canvas height")
    parser.add_argument("--width", default="100%", help="Canvas width")

    args = parser.parse_args()

    # Get Neo4j credentials from args or env
    neo4j_uri = args.neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = args.neo4j_user or os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = args.neo4j_password or os.getenv("NEO4J_PASSWORD", "your_neo4j_password")

    print(f"Connecting to Neo4j: {neo4j_uri}")

    visualizer = KGVisualizer(neo4j_uri, neo4j_user, neo4j_password)

    try:
        visualizer.visualize(output_file=args.output, height=args.height, width=args.width)
    finally:
        visualizer.close()


if __name__ == "__main__":
    main()
