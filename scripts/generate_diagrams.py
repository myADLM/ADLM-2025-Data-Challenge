#!/usr/bin/env python3
"""
Generate architecture diagrams for LabDocs Knowledge Graph system.
This script uses the diagrams library to create visual representations of the system architecture.

Run with: uv run --with diagrams scripts/generate_diagrams.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom
from pathlib import Path

# Node attributes for better text alignment
NODE_ATTR = {
    "shape": "box",
    "style": "rounded,filled",
    "fixedsize": "false",
    "fontname": "Arial",
    "fontsize": "11",
    "align": "center",
}

def create_label(text):
    """Create a properly aligned label using HTML-like formatting for Graphviz."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if len(lines) == 1:
        return text
    # Use HTML label format for better alignment
    # Graphviz HTML labels use <BR/> for line breaks
    # Escape special HTML characters
    def escape_html(s):
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    html_label = escape_html(lines[0])
    for line in lines[1:]:
        html_label += f"<BR/>{escape_html(line)}"
    return f"<{html_label}>"

# Output directory
OUTPUT_DIR = Path("docs/diagrams")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_system_architecture():
    """Generate the complete system architecture diagram."""
    print("Generating system architecture diagram...")
    
    with Diagram(
        "LabDocs Knowledge Graph System Architecture",
        filename=str(OUTPUT_DIR / "system_architecture"),
        show=False,
        direction="TB",
        graph_attr={"ratio": "1.33", "size": "16,12", "pad": "0.5", "fontname": "Arial"},
        node_attr=NODE_ATTR,
    ):
        # Input layer
        with Cluster("Input Layer"):
            pdf_files = Custom(create_label("PDF Files\n(SOP, FDA)"), "", **NODE_ATTR)
        
        # Processing pipeline
        with Cluster("Processing Pipeline"):
            with Cluster("Step 1: PDF Parsing"):
                pdf_parser = Custom(create_label("pdf_parser\n(OpenRouter API)"), "", **NODE_ATTR)
            
            with Cluster("Step 2: KG Extraction"):
                kg_extractor = Custom(create_label("01_extract.py\n(Bedrock LLM)"), "", **NODE_ATTR)
            
            with Cluster("Step 3: KG Loading"):
                kg_loader = Custom(create_label("02_load.py\n(Entity Dedup)"), "", **NODE_ATTR)
        
        # Storage layer
        with Cluster("Storage Layer"):
            neo4j = Custom(create_label("Neo4j\nGraph Database"), "", **NODE_ATTR)
            vector_store = Custom(create_label("Entity Vector\nStore"), "", **NODE_ATTR)
        
        # Query layer
        with Cluster("Query Layer"):
            with Cluster("API & Services"):
                flask_api = Custom(create_label("Flask API\n/kg/query\n/kg/chat"), "", **NODE_ATTR)
                kg_wrapper = Custom("kg_api_wrapper.py", "", **NODE_ATTR)
            
            frontend = Custom(create_label("React Frontend\n(Chat Interface)"), "", **NODE_ATTR)
        
        # External services
        bedrock = Custom(create_label("AWS Bedrock\n(LLM + Embeddings)"), "", **NODE_ATTR)
        
        # Connections
        pdf_files >> pdf_parser
        pdf_parser >> kg_extractor
        kg_extractor >> kg_loader
        kg_loader >> neo4j
        kg_loader >> vector_store
        
        kg_wrapper >> neo4j
        kg_wrapper >> vector_store
        kg_wrapper >> bedrock
        
        flask_api >> kg_wrapper
        frontend >> flask_api
        
        bedrock >> kg_extractor
        bedrock >> kg_loader
        bedrock >> kg_wrapper
    
    print(f"✓ System architecture diagram saved to {OUTPUT_DIR / 'system_architecture.png'}")


def generate_pipeline_flow():
    """Generate the knowledge graph pipeline flow diagram."""
    print("Generating pipeline flow diagram...")
    
    with Diagram(
        "Knowledge Graph Pipeline Flow",
        filename=str(OUTPUT_DIR / "pipeline_flow"),
        show=False,
        direction="LR",
        graph_attr={"ratio": "1.33", "size": "16,12", "pad": "0.5", "fontname": "Arial"},
        node_attr=NODE_ATTR,
    ):
        markdown = Custom(create_label("Markdown\nDocuments"), "", **NODE_ATTR)
        
        with Cluster("Extraction Phase"):
            extract = Custom(create_label("01_extract.py\nExtract entities\n& relationships"), "", **NODE_ATTR)
            json_files = Custom(create_label("JSON Files\n(entities + rels)"), "", **NODE_ATTR)
        
        with Cluster("Loading Phase"):
            load = Custom(create_label("02_load.py\nLoad into Neo4j\n+ Create embeddings"), "", **NODE_ATTR)
            neo4j = Custom(create_label("Neo4j\nGraph DB"), "", **NODE_ATTR)
            vectors = Custom(create_label("Entity Vector\nStore"), "", **NODE_ATTR)
        
        bedrock = Custom(create_label("AWS Bedrock\n(LLM + Embed)"), "", **NODE_ATTR)
        
        markdown >> extract
        extract >> json_files
        json_files >> load
        load >> neo4j
        load >> vectors
        bedrock >> extract
        bedrock >> load
    
    print(f"✓ Pipeline flow diagram saved to {OUTPUT_DIR / 'pipeline_flow.png'}")


def generate_query_flow():
    """Generate the query flow diagram."""
    print("Generating query flow diagram...")
    
    with Diagram(
        "Knowledge Graph Query Flow",
        filename=str(OUTPUT_DIR / "query_flow"),
        show=False,
        direction="TB",
        graph_attr={"ratio": "1.33", "size": "16,12", "pad": "0.5", "fontname": "Arial"},
        node_attr=NODE_ATTR,
    ):
        user = Custom("User Question", "", **NODE_ATTR)
        
        with Cluster("Query Processing"):
            semantic = Custom(create_label("Semantic Search\n(Entity Vector Store)"), "", **NODE_ATTR)
            graph_traversal = Custom(create_label("Graph Traversal\n(Neo4j Cypher)"), "", **NODE_ATTR)
            llm_synthesis = Custom(create_label("LLM Synthesis\n(Bedrock Converse)"), "", **NODE_ATTR)
        
        answer = Custom(create_label("Answer\n+ References"), "", **NODE_ATTR)
        
        neo4j = Custom(create_label("Neo4j\nGraph DB"), "", **NODE_ATTR)
        vectors = Custom(create_label("Entity Vector\nStore"), "", **NODE_ATTR)
        bedrock = Custom("AWS Bedrock\nLLM", "", **NODE_ATTR)
        
        user >> semantic
        semantic >> vectors
        semantic >> graph_traversal
        graph_traversal >> neo4j
        graph_traversal >> llm_synthesis
        llm_synthesis >> bedrock
        llm_synthesis >> answer
    
    print(f"✓ Query flow diagram saved to {OUTPUT_DIR / 'query_flow.png'}")


def main():
    """Generate all architecture diagrams."""
    print("=" * 60)
    print("Generating LabDocs Knowledge Graph Architecture Diagrams")
    print("=" * 60)
    print()
    
    try:
        generate_system_architecture()
        print()
        generate_pipeline_flow()
        print()
        generate_query_flow()
        print()
        print("=" * 60)
        print("✓ All diagrams generated successfully!")
        print(f"  Output directory: {OUTPUT_DIR.absolute()}")
        print("=" * 60)
    except Exception as e:
        print(f"Error generating diagrams: {e}")
        raise


if __name__ == "__main__":
    main()

