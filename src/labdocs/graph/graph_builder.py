"""Knowledge graph builder orchestrator using PropertyGraphIndex and Bedrock LLM."""
import argparse
import asyncio
import json
import os
import re
from pathlib import Path
from typing import Optional, List, Dict
from concurrent.futures import ThreadPoolExecutor
from jinja2 import Environment, FileSystemLoader
from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm
from dotenv import load_dotenv
import pandas as pd
from transformers import AutoTokenizer

from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.llms.bedrock_converse import BedrockConverse

from .config import GraphBuilderConfig, Neo4jConfig, DeduplicationConfig, SchemaConfig
from .graph_store_wrapper import GraphStoreWrapper
from .entity_deduplicator import EntityDeduplicator
from .schema_validator import SchemaValidator


class GraphBuilder:
    """
    Build knowledge graph from indexed documents using:
    - PropertyGraphIndex with SchemaLLMPathExtractor
    - Neo4j as graph store
    - Two-level entity deduplication (Levenshtein + LLM)
    """

    def __init__(self, config: GraphBuilderConfig, doc_type: str = "unified"):
        self.config = config
        self.vectordb_dir = Path(config.vectordb_dir)
        self.graphdb_dir = Path(config.graphdb_dir)
        self.graphdb_dir.mkdir(exist_ok=True)

        # Document type: 'unified' (both SOP and FDA in single graph), 'sop', or 'fda'
        self.doc_type = doc_type.lower()
        if self.doc_type not in ["unified", "sop", "fda"]:
            raise ValueError(f"Invalid doc_type: {doc_type}. Must be 'unified', 'sop', or 'fda'")

        # Initialize dataframes for tracking
        self.entities_df = pd.DataFrame(columns=[
            'entity_id', 'entity_type', 'title', 'description', 'source_document'
        ])
        self.relationships_df = pd.DataFrame(columns=[
            'source_id', 'target_id', 'relationship_type', 'source_text', 'source_document'
        ])

        # Load environment variables
        load_dotenv()

        # Initialize Bedrock LLM
        model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        aws_profile = os.getenv("AWS_PROFILE", "your_aws_profile_name")

        # Model-specific token limits (actual API limits)
        model_token_limits = {
            "ai21.jamba": 4096,
            "anthropic.claude": 4096,
            "meta.llama": 2048,
        }
        max_tokens = next(
            (limit for prefix, limit in model_token_limits.items() if prefix in model_id),
            4096
        )
        self.max_tokens = max_tokens

        # Initialize tokenizer for token counting
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

        print(f"Initializing Bedrock LLM: {model_id} (region: {aws_region}, max_tokens: {max_tokens})")

        self.bedrock_llm = BedrockConverse(
            model=model_id,
            region_name=aws_region,
            profile_name=aws_profile,
            temperature=0.0, # better for extraction/KG building
            max_tokens=max_tokens
        )

        # Initialize Bedrock embeddings
        embed_model = BedrockEmbedding(
            model_name="amazon.titan-embed-text-v2:0",
            region_name=aws_region,
            embed_batch_size=10
        )
        Settings.embed_model = embed_model

        # Initialize Neo4j graph store
        self.graph_store = GraphStoreWrapper(config.neo4j, config.graphdb_dir)

        # Initialize deduplicator and validator
        self.deduplicator = EntityDeduplicator(
            self.graph_store.store,
            self.bedrock_llm,
            config.deduplication
        )
        self.validator = SchemaValidator(config.schema)

        # Jinja2 environment for prompts
        self.jinja_env = Environment(
            loader=FileSystemLoader(Path(__file__).parent.parent / "prompts")
        )

        # Thread pool for running sync Bedrock calls in async context
        self.thread_pool = ThreadPoolExecutor(max_workers=5)

    def get_documents_to_process(self) -> set:
        """
        Return documents indexed in vectordb but not yet in graphdb.
        """
        try:
            vectordb_processed = self._get_vectordb_processed()
            graphdb_processed = self.graph_store.get_processed_documents()
            return vectordb_processed - graphdb_processed
        except Exception as e:
            print(f"Error getting documents to process: {e}")
            return set()

    def _get_vectordb_processed(self) -> set:
        """Load set of documents processed in vectordb."""
        try:
            persist_dir = self.vectordb_dir
            if persist_dir.exists() and (persist_dir / "docstore.json").exists():
                storage_context = StorageContext.from_defaults(persist_dir=str(persist_dir))
                index = load_index_from_storage(storage_context)

                processed = set()
                for node_id in index.docstore.docs:
                    node = index.docstore.get_document(node_id)
                    if node.metadata and "filename" in node.metadata:
                        processed.add(node.metadata["filename"])
                return processed
        except Exception as e:
            print(f"Warning: Could not load vectordb documents: {e}")

        return set()

    def load_chunks_from_vectordb(self, document_path: str):
        """
        Load document chunks from vectordb by document filename.
        """
        try:
            persist_dir = self.vectordb_dir
            storage_context = StorageContext.from_defaults(persist_dir=str(persist_dir))
            index = load_index_from_storage(storage_context)

            chunks = []
            for node_id in index.docstore.docs:
                node = index.docstore.get_document(node_id)
                if (node.metadata and node.metadata.get("filename") == document_path):
                    chunks.append(node)

            return chunks
        except Exception as e:
            print(f"Error loading chunks for {document_path}: {e}")
            return []

    def check_document_token_count(self, chunks) -> bool:
        """
        Check if document chunks exceed max token limit.
        Returns True if document is within limits, False if it exceeds.
        """
        total_text = " ".join([chunk.get_content() for chunk in chunks])
        token_count = len(self.tokenizer.encode(total_text))

        if token_count > self.max_tokens:
            print(f"  Skipping document: {token_count} tokens exceeds {self.max_tokens} token limit")
            return False

        return True

    def _parse_json_response(self, json_str: str) -> Optional[dict]:
        """
        Parse JSON from Bedrock response.
        Handles markdown-wrapped JSON (```json ... ```).
        """
        # Remove markdown code block wrappers if present
        json_str = re.sub(r'^```(?:json)?\s*\n?', '', json_str)
        json_str = re.sub(r'\n?```\s*$', '', json_str)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None

    def extract_entities(self, chunks, doc_type_hint: str = None):
        """
        Extract entities and relationships from document chunks using Bedrock.
        Returns parsed JSON-LD extraction result.
        Uses unified schema (both SOP and FDA) or document-type specific schema.

        Args:
            chunks: Document chunks to extract from
            doc_type_hint: Optional hint for document type ('sop' or 'fda') when using unified schema
        """
        if not chunks:
            return {"@graph": []}

        # Combine chunk texts
        combined_text = "\n\n".join([
            f"## {chunk.metadata.get('filename', 'Unknown')}\n{chunk.text}"
            for chunk in chunks
        ])

        # Load ontology schema based on document type
        schema_filename = f"{self.doc_type}_ontology_schema.json"
        schema_path = Path(__file__).parent.parent / "prompts" / schema_filename
        with open(schema_path, 'r') as f:
            ontology = json.load(f)

        schema_text = json.dumps(ontology, indent=2)

        # Render extraction prompt based on document type
        user_template_name = f"{self.doc_type}_kg_extraction_user.j2"
        system_template_name = f"{self.doc_type}_kg_extraction_system.j2"

        user_prompt_template = self.jinja_env.get_template(user_template_name)
        system_prompt_template = self.jinja_env.get_template(system_template_name)

        system_prompt = system_prompt_template.render()
        user_prompt = user_prompt_template.render(
            schema_text=schema_text,
            markdown_content=combined_text
        )

        # Call Bedrock LLM
        try:
            response = self.bedrock_llm.complete(user_prompt)
            response_text = response.text if hasattr(response, 'text') else str(response)

            # Extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                extraction_result = self._parse_json_response(json_str)

                if extraction_result:
                    return extraction_result
                else:
                    print(f"Warning: Could not parse JSON from Bedrock")
                    return {"@graph": []}
            else:
                print(f"Warning: Could not find JSON in Bedrock response")
                return {"@graph": []}

        except Exception as e:
            print(f"Error calling Bedrock LLM: {e}")
            return {"@graph": []}

    def _collect_entities_to_dataframe(self, entities: list, source_document: str):
        """
        Collect extracted entities into dataframe.
        """
        rows = []
        for entity in entities:
            rows.append({
                'entity_id': entity.get('@id'),
                'entity_type': entity.get('@type'),
                'title': entity.get('title'),
                'description': entity.get('description', ''),
                'source_document': source_document
            })

        if rows:
            new_df = pd.DataFrame(rows)
            self.entities_df = pd.concat([self.entities_df, new_df], ignore_index=True)

    def _collect_relationships_to_dataframe(self, relationships: list, source_document: str):
        """
        Collect extracted relationships into dataframe.
        """
        rows = []
        for rel in relationships:
            rows.append({
                'source_id': rel.get('source_id'),
                'target_id': rel.get('target_id'),
                'relationship_type': rel.get('type'),
                'source_text': rel.get('source_text', ''),
                'source_document': source_document
            })

        if rows:
            new_df = pd.DataFrame(rows)
            self.relationships_df = pd.concat([self.relationships_df, new_df], ignore_index=True)

    def save_dataframes(self):
        """
        Save entities and relationships to JSON files in graphdb directory.
        Creates a JSON file per document with entities and relationships.
        """
        (self.graphdb_dir / "extractions").mkdir(exist_ok=True)

        # Group by source document and save as JSON
        if not self.entities_df.empty:
            for source_doc in self.entities_df['source_document'].unique():
                doc_entities = self.entities_df[self.entities_df['source_document'] == source_doc]
                doc_relationships = self.relationships_df[self.relationships_df['source_document'] == source_doc]

                extraction = {
                    'document': source_doc,
                    'entities': doc_entities.to_dict('records'),
                    'relationships': doc_relationships.to_dict('records')
                }

                # Clean filename
                safe_name = source_doc.replace('/', '_').replace('.', '_')
                output_file = self.graphdb_dir / "extractions" / f"{safe_name}.json"
                with open(output_file, 'w') as f:
                    json.dump(extraction, f, indent=2)

        # Also save combined summary
        summary = {
            'total_entities': len(self.entities_df),
            'total_relationships': len(self.relationships_df),
            'documents_processed': self.entities_df['source_document'].nunique() if not self.entities_df.empty else 0,
            'entity_types': self.entities_df['entity_type'].unique().tolist() if not self.entities_df.empty else [],
            'relationship_types': self.relationships_df['relationship_type'].unique().tolist() if not self.relationships_df.empty else []
        }
        summary_file = self.graphdb_dir / "summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"✓ Saved {len(self.entities_df)} entities to {self.graphdb_dir}/extractions/")
        print(f"✓ Saved {len(self.relationships_df)} relationships")
        print(f"✓ Summary saved to {summary_file}")

    def _print_dedup_stats(self, entity_stats: dict, rel_stats: dict):
        """Print deduplication statistics in a readable format."""
        print("\n" + "=" * 70)
        print("DEDUPLICATION STATISTICS")
        print("=" * 70)

        print("\nENTITY DEDUPLICATION (Classical Approach):")
        print(f"  Total extracted:        {entity_stats.get('total_extracted', 0)}")
        print(f"  Exact ID matches:       {entity_stats.get('exact_matches', 0)}")
        print(f"  Levenshtein matches:    {entity_stats.get('levenshtein_matches', 0)}")
        classical_matched = entity_stats.get('exact_matches', 0) + entity_stats.get('levenshtein_matches', 0)
        print(f"  Classical total:        {classical_matched}")

        print("\nENTITY DEDUPLICATION (LLM Approach):")
        print(f"  Had candidates:         {entity_stats.get('had_candidates', 0)}")
        print(f"  Sent to LLM:            {entity_stats.get('llm_sent_to_confirm', 0)}")
        print(f"  LLM confirmed:          {entity_stats.get('llm_confirmed', 0)}")
        print(f"  LLM rejected:           {entity_stats.get('llm_rejected', 0)}")

        print("\nENTITY DEDUPLICATION (Results):")
        print(f"  New entities:           {entity_stats.get('new_entities', 0)}")
        print(f"  Final count:            {classical_matched + entity_stats.get('llm_confirmed', 0) + entity_stats.get('new_entities', 0)}")

        print("\nRELATIONSHIP DEDUPLICATION:")
        print(f"  Existing (skipped):     {rel_stats.get('existing', 0)}")
        print(f"  New relationships:      {rel_stats.get('new', 0)}")
        print("=" * 70 + "\n")

    def build_graph(self, document_list=None, max_docs: int = 0):
        """
        Main entry point. Process unprocessed documents or specific list.

        Args:
            document_list: List of document paths to process. If None, processes all new docs.
            max_docs: Limit number of documents to process (0 = unlimited).
        """
        if document_list is None:
            document_list = self.get_documents_to_process()

        if not document_list:
            print("No new documents to process")
            return

        document_list = list(document_list)
        if max_docs > 0:
            document_list = document_list[:max_docs]

        print(f"Processing {len(document_list)} documents for knowledge graph")

        for doc_path in tqdm(document_list, desc="Building graph"):
            try:
                # Load chunks from vectordb
                chunks = self.load_chunks_from_vectordb(doc_path)
                if not chunks:
                    print(f"No chunks found for {doc_path}")
                    continue

                # Check token count limit
                if not self.check_document_token_count(chunks):
                    continue

                # Extract entities and relationships
                extraction_result = self.extract_entities(chunks)

                # Validate against schema
                validated, val_stats = self.validator.validate_extraction(extraction_result)

                if val_stats["invalid_entities"] > 0 or val_stats["invalid_relationships"] > 0:
                    print(f"Warning: {val_stats['invalid_entities']} invalid entities, "
                          f"{val_stats['invalid_relationships']} invalid relationships")

                # Deduplicate entities
                dedup_entities, dedup_stats = self.deduplicator.deduplicate(validated["entities"])

                # Deduplicate relationships
                dedup_rels, rel_stats = self.deduplicator.deduplicate_relationships(
                    validated["relationships"]
                )

                # Collect to dataframes
                self._collect_entities_to_dataframe(dedup_entities, doc_path)
                self._collect_relationships_to_dataframe(dedup_rels, doc_path)

                # Track processing
                self.graph_store.mark_document_processed(
                    doc_path,
                    entity_count=len(dedup_entities),
                    relationship_count=len(dedup_rels),
                    extraction_model="bedrock/claude-3-sonnet",
                    dedup_stats={
                        **dedup_stats,
                        "validation": val_stats
                    }
                )

                # Print dedup stats for this document
                self._print_dedup_stats(dedup_stats, rel_stats)
                print(f"✓ {doc_path}: {len(dedup_entities)} final entities, {len(dedup_rels)} final relationships")

            except Exception as e:
                print(f"✗ Error processing {doc_path}: {e}")
                continue

        print("Graph building complete")

    async def process_document_async(self, doc_path: str, semaphore: asyncio.Semaphore) -> Optional[Dict]:
        """
        Process single document asynchronously.
        Semaphore controls concurrency to avoid API rate limits.
        """
        async with semaphore:
            try:
                # Load chunks from vectordb
                chunks = self.load_chunks_from_vectordb(doc_path)
                if not chunks:
                    return None

                # Check token count limit
                if not self.check_document_token_count(chunks):
                    return None

                # Extract entities and relationships (run sync call in thread pool)
                loop = asyncio.get_event_loop()
                extraction_result = await loop.run_in_executor(
                    self.thread_pool,
                    self.extract_entities,
                    chunks
                )

                # Validate against schema
                validated, val_stats = self.validator.validate_extraction(extraction_result)

                if val_stats["invalid_entities"] > 0 or val_stats["invalid_relationships"] > 0:
                    print(f"Warning: {val_stats['invalid_entities']} invalid entities, "
                          f"{val_stats['invalid_relationships']} invalid relationships in {doc_path}")

                # Deduplicate entities
                dedup_entities, dedup_stats = self.deduplicator.deduplicate(validated["entities"])

                # Deduplicate relationships
                dedup_rels, rel_stats = self.deduplicator.deduplicate_relationships(
                    validated["relationships"]
                )

                # Track processing
                self.graph_store.mark_document_processed(
                    doc_path,
                    entity_count=len(dedup_entities),
                    relationship_count=len(dedup_rels),
                    extraction_model="bedrock/claude-3-sonnet",
                    dedup_stats={
                        **dedup_stats,
                        "validation": val_stats
                    }
                )

                return {
                    'doc_path': doc_path,
                    'entities': dedup_entities,
                    'relationships': dedup_rels,
                    'dedup_stats': dedup_stats,
                    'rel_stats': rel_stats
                }

            except Exception as e:
                print(f"✗ Error processing {doc_path}: {e}")
                return None

    async def build_graph_async(self, document_list: List[str], max_concurrent: int = 5) -> None:
        """
        Process multiple documents concurrently using asyncio.

        Args:
            document_list: List of document paths to process
            max_concurrent: Maximum number of concurrent Bedrock API calls (default: 5)
        """
        if not document_list:
            print("No documents to process")
            return

        document_list = list(document_list)
        print(f"Processing {len(document_list)} documents concurrently (max_concurrent={max_concurrent})")

        # Create semaphore to limit concurrent API calls
        semaphore = asyncio.Semaphore(max_concurrent)

        # Create tasks for all documents
        tasks = [
            self.process_document_async(doc_path, semaphore)
            for doc_path in document_list
        ]

        # Process with async tqdm progress bar
        results = await atqdm.gather(*tasks, desc="Building graph (async)")

        # Collect results
        successful = 0
        for result in results:
            if result:
                self._collect_entities_to_dataframe(result['entities'], result['doc_path'])
                self._collect_relationships_to_dataframe(result['relationships'], result['doc_path'])
                self._print_dedup_stats(result['dedup_stats'], result['rel_stats'])
                print(f"✓ {result['doc_path']}: {len(result['entities'])} entities, {len(result['relationships'])} relationships")
                successful += 1

        print(f"\nAsync graph building complete: {successful}/{len(document_list)} documents processed successfully")

    def close(self):
        """Close connections."""
        self.graph_store.close()
        self.thread_pool.shutdown(wait=True)


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Build knowledge graph from indexed documents")
    parser.add_argument("--vectordb-dir", default="./vectordb", help="Vector database directory")
    parser.add_argument("--graphdb-dir", default="./graphdb", help="Graph database directory")
    parser.add_argument("--neo4j-uri", default=None, help="Neo4j connection URI")
    parser.add_argument("--neo4j-user", default=None, help="Neo4j username")
    parser.add_argument("--neo4j-password", default=None, help="Neo4j password")
    parser.add_argument("--all-documents", action="store_true", help="Process all docs (not just new)")
    parser.add_argument("--max-docs", type=int, default=0, help="Limit document count")
    parser.add_argument("--async", dest="use_async", action="store_true",
                        help="Use async batch processing for concurrent document extraction")
    parser.add_argument("--max-concurrent", type=int, default=5,
                        help="Maximum concurrent Bedrock API calls (default: 5)")

    args = parser.parse_args()

    # Use env vars as defaults, override with CLI args if provided
    neo4j_uri = args.neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = args.neo4j_user or os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = args.neo4j_password or os.getenv("NEO4J_PASSWORD", "your_neo4j_password")

    config = GraphBuilderConfig(
        vectordb_dir=args.vectordb_dir,
        graphdb_dir=args.graphdb_dir,
        neo4j=Neo4jConfig(
            uri=neo4j_uri,
            username=neo4j_user,
            password=neo4j_password
        )
    )

    builder = GraphBuilder(config)

    try:
        docs_to_process = None
        if args.all_documents:
            # When --all-documents is set, load documents from vectordb but don't filter
            docs_to_process = builder._get_vectordb_processed()
        else:
            docs_to_process = builder.get_documents_to_process()

        if docs_to_process:
            docs_to_process = list(docs_to_process)
            if args.max_docs > 0:
                docs_to_process = docs_to_process[:args.max_docs]

        if args.use_async:
            # Use async batch processing
            asyncio.run(builder.build_graph_async(docs_to_process, max_concurrent=args.max_concurrent))
        else:
            # Use synchronous sequential processing (original behavior)
            builder.build_graph(docs_to_process, max_docs=args.max_docs)

        builder.save_dataframes()
    finally:
        builder.close()


if __name__ == "__main__":
    main()
