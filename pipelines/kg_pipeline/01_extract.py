#!/usr/bin/env python3
"""
Extract entities and relationships from laboratory markdown documents.
Uses unified ontology with structured validation and comprehensive error handling.

Usage:
    uv run pipelines/kg_pipeline/01_extract.py --input-folder <input_directory> --output-dir <output_directory>

Examples:
    uv run pipelines/kg_pipeline/01_extract.py --input-folder "data/parsed/LabDocs/FDA/Molecular Genetics" --output-dir graphdb_unified
    uv run pipelines/kg_pipeline/01_extract.py --input-folder data/parsed/LabDocs/Procedures --output-dir graphdb_unified --max-docs 10
    uv run pipelines/kg_pipeline/01_extract.py --input-folder data/parsed/LabDocs/Procedures --output-dir graphdb_unified
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Set

import boto3
from botocore.config import Config
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from llama_index.core import SimpleDirectoryReader
from llama_index.llms.bedrock_converse import BedrockConverse
from botocore.exceptions import ClientError, BotoCoreError

from logger import setup_logger

# Constants
MAX_CHARS = 80000
PROMPTS_DIR = "src/labdocs/prompts"
SCHEMA_FILE = "unified_ontology_schema.json"
MAX_TOKENS = 8192
MAX_RETRIES = 3  # max number of retries for API calls
RETRY_DELAY = 5  # delay between retries in seconds
REQUEST_TIMEOUT = 300  # request timeout in seconds (5 minutes)

# set environment defaults
os.environ.setdefault('BEDROCK_MODEL_ID', 'openai.gpt-oss-120b-1:0')

# initialize logger
logger = setup_logger("kg_pipeline.extract")


def get_processed_documents(output_dir: Path) -> Set[str]:
    """Get set of already processed document names."""
    if not output_dir.exists():
        return set()
    return {f.stem for f in output_dir.glob("*.json")}

# tiny workaround
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
    # get document path and name
    doc_path = doc.metadata.get('file_path', '')
    rel_path = doc_path if doc_path else doc.metadata.get('filename', f'doc_{doc_idx}')
    doc_name = Path(rel_path).stem
    
    logger.info(f"Processing [{doc_idx + 1}/{total_docs}]: {rel_path}")
    
    # truncate text if needed
    text = doc.get_content()
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS]
        logger.info(f"  Truncated to {MAX_CHARS} characters (~{MAX_CHARS // 4} tokens)")
    
    try:
        # generate prompts
        user_template = jinja_env.get_template("unified_kg_extraction_user.j2")
        # system_template = jinja_env.get_template("unified_kg_extraction_system.j2")
        
        # system_prompt = system_template.render()
        user_prompt = user_template.render(
            schema_text=schema_text, 
            markdown_content=doc.get_content()
        )
        
        # get llm response with retry logic
        response_text = None
        last_error = None
        
        # log prompt size for debugging
        prompt_size = len(user_prompt)
        logger.info(f"  Sending request to Bedrock (prompt size: {prompt_size:,} chars)...")
        start_time = time.time()
        
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"  Attempt {attempt + 1}/{MAX_RETRIES} for {doc_name} (started at {time.strftime('%H:%M:%S')})")
                response = bedrock_llm.complete(user_prompt)
                elapsed_time = time.time() - start_time
                logger.info(f"  [OK] Received response from Bedrock in {elapsed_time:.1f} seconds")
                response_text = response.text if hasattr(response, 'text') else str(response)
                break  # success, exit retry loop
            except (ClientError, BotoCoreError) as e:
                last_error = e
                error_code = getattr(e, 'response', {}).get('Error', {}).get('Code', 'Unknown')
                error_message = str(e)
                
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_DELAY * (attempt + 1)  # exponential backoff
                    logger.warning(
                        f"  Bedrock API error (attempt {attempt + 1}/{MAX_RETRIES}): {error_code} - {error_message}. "
                        f"Retrying in {wait_time} seconds..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"  Failed after {MAX_RETRIES} attempts: {error_code} - {error_message}")
                    raise
            except Exception as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_DELAY * (attempt + 1)
                    logger.warning(
                        f"  Unexpected error (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}. "
                        f"Retrying in {wait_time} seconds..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"  Failed after {MAX_RETRIES} attempts: {str(e)}")
                    raise
        
        if response_text is None:
            raise Exception(f"Failed to get response from Bedrock after {MAX_RETRIES} attempts: {last_error}")
        
        # parse results
        result = parse_json_response(response_text)
        if result and result.get("@graph"):
            entities, relationships = result["@graph"], result.get("relationships", [])
        else:
            entities, relationships = None, None
        
        if entities:
            logger.info(f"  Extracted {len(entities)} entities")
            
            # save to json file
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
            
    except (ClientError, BotoCoreError) as e:
        error_code = getattr(e, 'response', {}).get('Error', {}).get('Code', 'Unknown')
        logger.error(f"  AWS/Bedrock error processing {doc_name}: {error_code} - {str(e)}")
        logger.error(f"  This might be a timeout, rate limit, or authentication issue. Check your AWS credentials and Bedrock access.")
        return False
    except Exception as e:
        logger.error(f"  Error processing {doc_name}: {e}", exc_info=True)
        return False


def main():
    load_dotenv()
    
    try:
        args = setup_args()
        
        # setup directories
        source_dir = Path(args.input_folder)
        if not source_dir.exists():
            raise FileNotFoundError(f"Input folder not found: {source_dir}")
        
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)
        extractions_dir = output_dir / "extractions"
        extractions_dir.mkdir(exist_ok=True)
        
        # load documents
        logger.info(f"Loading documents from: {source_dir}")
        documents = SimpleDirectoryReader(input_dir=str(source_dir)).load_data()
        
        if not documents:
            logger.error(f"No documents found in {source_dir}")
            return 1
        
        # get already processed documents
        processed_docs = get_processed_documents(extractions_dir)

        # filter out already processed documents
        unprocessed_docs = []
        for doc in documents:
            doc_path = doc.metadata.get('file_path', '')
            doc_name = Path(doc_path).stem if doc_path else doc.metadata.get('filename', 'unknown')
            if doc_name not in processed_docs:
                unprocessed_docs.append(doc)
        
        # apply limit to unprocessed documents
        if args.max_docs > 0:
            unprocessed_docs = unprocessed_docs[:args.max_docs]

        logger.info(f"Total documents: {len(documents)}")
        logger.info(f"Already processed: {len(processed_docs)}")
        logger.info(f"Processing: {len(unprocessed_docs)} new documents")
        logger.info(f"Output directory: {output_dir}")

        if not unprocessed_docs:
            logger.info("No new documents to process")
            return 0
        
        # initialize llm and templates
        model_id = os.getenv("BEDROCK_MODEL_ID")
        aws_region = os.getenv("AWS_REGION")
        aws_profile = os.getenv("AWS_PROFILE")
        
        logger.info(f"Initializing Bedrock LLM (model: {model_id}, region: {aws_region}, profile: {aws_profile})")
        
        boto_config = Config(
            connect_timeout=300,
            read_timeout=300
        )
        
        # create a session with the config
        # session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
        
        bedrock_llm = BedrockConverse(
            model=model_id,
            region_name=aws_region,
            profile_name=aws_profile,
            temperature=0.0,
            max_tokens=MAX_TOKENS
        )
        
        # Patch the client's config after creation to increase timeout
        # This is necessary because BedrockConverse creates its own client with default timeouts
        if hasattr(bedrock_llm, '_client'):
            original_config = bedrock_llm._client._client_config
            logger.debug(f"Original timeout: connect={original_config.connect_timeout}s, read={original_config.read_timeout}s")
            
            # Update the config
            bedrock_llm._client._client_config = boto_config
            
            # Also update the endpoint's HTTP adapter timeout if it exists
            if hasattr(bedrock_llm._client, '_endpoint') and hasattr(bedrock_llm._client._endpoint, 'http_session'):
                http_session = bedrock_llm._client._endpoint.http_session
                if hasattr(http_session, 'timeout'):
                    http_session.timeout = (boto_config.connect_timeout, boto_config.read_timeout)
            
            logger.info(f"Configured Bedrock client timeout: connect={boto_config.connect_timeout}s, read={boto_config.read_timeout}s")
        
        logger.info("Bedrock LLM initialized successfully")
        
        jinja_env = Environment(loader=FileSystemLoader(PROMPTS_DIR))
        schema_text = load_schema()
        
        # process documents
        processed_count = 0
        for idx, doc in enumerate(unprocessed_docs):
            success = process_document(
                doc, idx, len(unprocessed_docs), bedrock_llm, jinja_env, 
                schema_text, extractions_dir
            )
            if success:
                processed_count += 1
        
        # summary
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
