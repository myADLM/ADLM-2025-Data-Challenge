#!/usr/bin/env python3
"""
Extract entities and relationships from laboratory markdown documents.
Uses unified ontology with structured validation and comprehensive error handling.

Usage:
    python 01_extract.py --input-folder <input_directory> --output-dir <output_directory>

Examples:
    python 01_extract.py --input-folder "data/parsed/LabDocs/FDA/Molecular Genetics" --output-dir graphdb_unified
    python 01_extract.py --input-folder data/parsed/LabDocs/Procedures --output-dir graphdb_unified --max-docs 10
    python 01_extract.py --input-folder data/parsed/LabDocs/Procedures --output-dir graphdb_unified
"""
import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Set

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from llama_index.core import SimpleDirectoryReader
from llama_index.llms.bedrock_converse import BedrockConverse

# Constants
MAX_CHARS = 80000  # Higher limit for better extraction
PROMPTS_DIR = "src/labdocs/prompts"
SCHEMA_FILE = "unified_ontology_schema.json"
MAX_TOKENS = 4096  # Model limit for Jamba

# Set environment defaults
os.environ.setdefault('BEDROCK_MODEL_ID', 'ai21.jamba-1-5-large-v1:0')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_processed_documents(output_dir: Path) -> Set[str]:
    """Get set of already processed document names."""
    if not output_dir.exists():
        return set()
    return {f.stem for f in output_dir.glob("*.json")}


def parse_json_response(response_text):
    """Extract JSON from LLM response text (fallback method)."""
    if not response_text or '{' not in response_text:
        return None
    
    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1
    
    try:
        return json.loads(response_text[json_start:json_end])
    except (json.JSONDecodeError, ValueError):
        logger.warning("Failed to parse JSON from response text")
        return None


def setup_args():
    """Setup command line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract entities and relationships from markdown documents using unified ontology"
    )
    parser.add_argument(
        "--input-folder",
        required=True,
        help="Directory containing markdown documents to process"
    )
    parser.add_argument(
        "--output-dir", 
        required=True,
        help="Output directory for extracted JSON files"
    )
    parser.add_argument(
        "--max-docs", 
        type=int,
        default=0,
        help="Limit number of documents to process (0 = process all)"
    )
    return parser.parse_args()


def load_schema():
    """Load ontology schema."""
    schema_path = Path(PROMPTS_DIR) / SCHEMA_FILE
    with open(schema_path) as f:
        ontology = json.load(f)
    return json.dumps(ontology, indent=2)


def process_document(doc, doc_idx, total_docs, bedrock_llm, jinja_env, schema_text, 
                    extractions_dir):
    """Process a single document with improved error handling."""
    # Get document path and name
    doc_path = doc.metadata.get('file_path', '')
    rel_path = doc_path if doc_path else doc.metadata.get('filename', f'doc_{doc_idx}')
    doc_name = Path(rel_path).stem
    
    logger.info(f"Processing [{doc_idx + 1}/{total_docs}]: {rel_path}")
    
    # Truncate text if needed
    text = doc.get_content()
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS]
        logger.info(f"  Truncated to {MAX_CHARS} characters (~{MAX_CHARS // 4} tokens)")
    
    try:
        # Generate prompts
        user_template = jinja_env.get_template("unified_kg_extraction_user.j2")
        system_template = jinja_env.get_template("unified_kg_extraction_system.j2")
        
        system_prompt = system_template.render()
        user_prompt = user_template.render(schema_text=schema_text, markdown_content=doc.get_content())
        
        # Get LLM response
        response = bedrock_llm.complete(user_prompt)
        response_text = response.text if hasattr(response, 'text') else str(response)
        
        # Parse results
        result = parse_json_response(response_text)
        if result and result.get("@graph"):
            entities, relationships = result["@graph"], result.get("relationships", [])
        else:
            entities, relationships = None, None
        
        if entities:
            logger.info(f"  Extracted {len(entities)} entities")
            
            # Save to JSON file
            output_file = extractions_dir / f"{doc_name}.json"
            output_data = {
                "source_document": rel_path,
                "entities": entities,
                "relationships": relationships or []
            }
            
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            logger.info(f"  Saved to: {output_file}")
            return True
        else:
            logger.warning(f"  No valid entities extracted from {doc_name}")
            return False
            
    except Exception as e:
        logger.error(f"  Error processing {doc_name}: {e}")
        return False


def main():
    load_dotenv()
    
    try:
        args = setup_args()
        
        # Setup directories
        source_dir = Path(args.input_folder)
        if not source_dir.exists():
            raise FileNotFoundError(f"Input folder not found: {source_dir}")
        
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)
        extractions_dir = output_dir / "extractions"
        extractions_dir.mkdir(exist_ok=True)
        
        # Load documents
        logger.info(f"Loading documents from: {source_dir}")
        documents = SimpleDirectoryReader(input_dir=str(source_dir)).load_data()
        
        if not documents:
            logger.error(f"No documents found in {source_dir}")
            return 1
        
        # Get already processed documents
        processed_docs = get_processed_documents(extractions_dir)
        
        # Filter out already processed documents
        unprocessed_docs = []
        for doc in documents:
            doc_path = doc.metadata.get('file_path', '')
            doc_name = Path(doc_path).stem if doc_path else doc.metadata.get('filename', 'unknown')
            if doc_name not in processed_docs:
                unprocessed_docs.append(doc)
        
        # Apply limit to unprocessed documents
        if args.max_docs > 0:
            unprocessed_docs = unprocessed_docs[:args.max_docs]
        
        logger.info(f"Total documents: {len(documents)}")
        logger.info(f"Already processed: {len(processed_docs)}")
        logger.info(f"Processing: {len(unprocessed_docs)} new documents")
        logger.info(f"Output directory: {output_dir}")
        
        if not unprocessed_docs:
            logger.info("No new documents to process")
            return 0
        
        # Initialize LLM and templates
        bedrock_llm = BedrockConverse(
            model=os.getenv("BEDROCK_MODEL_ID"),
            region_name=os.getenv("AWS_REGION"),
            profile_name=os.getenv("AWS_PROFILE"),
            temperature=0.0,
            max_tokens=MAX_TOKENS
        )
        
        jinja_env = Environment(loader=FileSystemLoader(PROMPTS_DIR))
        schema_text = load_schema()
        
        # Process documents
        processed_count = 0
        for idx, doc in enumerate(unprocessed_docs):
            success = process_document(
                doc, idx, len(unprocessed_docs), bedrock_llm, jinja_env, 
                schema_text, extractions_dir
            )
            if success:
                processed_count += 1
        
        # Summary
        logger.info("="*70)
        logger.info(f"Processing complete: {processed_count}/{len(unprocessed_docs)} new documents processed")
        logger.info(f"Total processed documents: {len(processed_docs) + processed_count}")
        logger.info(f"Extractions saved to: {extractions_dir}")
        logger.info("="*70)
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
