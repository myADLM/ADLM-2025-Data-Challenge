import os
import sys
import re
import json
from pathlib import Path

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv

from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.llms.bedrock_converse import BedrockConverse

# Add kg_pipeline directory to path for imports
kg_pipeline_dir = Path(__file__).parent.parent.parent / "pipelines" / "kg_pipeline"
if str(kg_pipeline_dir) not in sys.path:
    sys.path.insert(0, str(kg_pipeline_dir))

from kg_api_wrapper import (
    get_graph_store,
    get_bedrock_llm as get_kg_bedrock_llm,
    query_knowledge_graph,
    retrieve_context_from_graph
)

# In-memory chat sessions (in production, use Redis or database)
chat_sessions = {}

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global query engine (initialized once at startup)
query_engine = None

# Global KG components (initialized once at startup)
kg_graph_store = None
kg_llm = None

def setup_llm():
    model_id = os.getenv("BEDROCK_MODEL_ID")
    aws_profile = os.getenv("AWS_PROFILE")
    region = os.getenv("AWS_REGION")

    llm = BedrockConverse(
        model=model_id,
        region_name=region,
        profile_name=aws_profile,
        temperature=0.1,
        max_tokens=2048
    )
    return llm

def initialize_query_engine(persist_dir="./vectordb", top_k=5):
    global query_engine

    embed_model = BedrockEmbedding(
        model_name=os.getenv("EMBEDDING_MODEL_BEDROCK", "amazon.titan-embed-text-v2:0"),
        region_name=os.getenv("AWS_REGION"),
        profile_name=os.getenv("AWS_PROFILE")
    )
    Settings.embed_model = embed_model

    Settings.llm = setup_llm()

    persist_path = Path(persist_dir)
    if not persist_path.exists():
        raise ValueError(f"Index directory not found: {persist_dir}")

    storage_context = StorageContext.from_defaults(persist_dir=str(persist_path))
    index = load_index_from_storage(storage_context)

    query_engine = index.as_query_engine(
        similarity_top_k=top_k,
        verbose=False
    )

def initialize_kg_components():
    """
    Initialize knowledge graph components (Neo4j graph store and Bedrock LLM).
    """
    global kg_graph_store, kg_llm
    
    if kg_graph_store is None:
        try:
            kg_graph_store = get_graph_store()
        except Exception as e:
            raise ValueError(f"Failed to initialize graph store: {str(e)}")
    
    if kg_llm is None:
        try:
            kg_llm = get_kg_bedrock_llm()
        except Exception as e:
            raise ValueError(f"Failed to initialize KG LLM: {str(e)}")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/query', methods=['POST'])
def query():
    global query_engine

    if query_engine is None:
        try:
            initialize_query_engine()
        except Exception as e:
            return jsonify({"error": f"Failed to initialize query engine: {str(e)}"}), 500

    data = request.json
    question = data.get('question', '').strip()

    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        response = query_engine.query(question)

        sources = []
        if hasattr(response, 'source_nodes') and response.source_nodes:
            for node in response.source_nodes:
                metadata = node.node.metadata
                sources.append({
                    'filename': metadata.get('filename', 'Unknown'),
                    'filepath': metadata.get('filepath', 'Unknown'),
                    'score': node.score if hasattr(node, 'score') else 0.0,
                    'preview': node.node.text.replace('\n', ' ')[:200]
                })

        return jsonify({
            'question': question,
            'answer': response.response,
            'sources': sources
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/document/<filename>', methods=['GET'])
def get_document(filename):
    segment = request.args.get('segment', '')
    filepath = request.args.get('filepath', '')

    if not filename:
        return jsonify({"error": "Filename is required"}), 400

    # Try to find document in Procedures or FDA folders
    doc_path = None
    if filepath:
        # Use provided filepath - it may be relative or absolute
        doc_path = Path(filepath)
        
        # If it's not absolute, check if it starts with "data/parsed" or "./data/parsed"
        if not doc_path.is_absolute():
            # Remove leading "./" if present
            clean_path = filepath.lstrip("./")
            
            # If it already starts with "data/parsed", use it as-is (relative to workspace root)
            if clean_path.startswith("data/parsed"):
                doc_path = Path("./") / clean_path
            # Otherwise, assume it's relative to data/parsed/LabDocs
            else:
                doc_path = Path("./data/parsed/LabDocs") / clean_path
        
        # Debug logging (can be removed in production)
        import logging
        logging.debug(f"Resolving document: filename={filename}, filepath={filepath}, resolved={doc_path}")
    else:
        # Try Procedures first, then FDA subdirectories
        procedures_path = Path("./data/parsed/LabDocs/Procedures") / filename
        if procedures_path.exists():
            doc_path = procedures_path
        else:
            # Search in FDA subdirectories
            fda_base = Path("./data/parsed/LabDocs/FDA")
            for fda_subdir in fda_base.rglob(filename):
                if fda_subdir.is_file():
                    doc_path = fda_subdir
                    break

    # If still not found, try fuzzy matching by normalizing the filename
    if not doc_path or not doc_path.exists():
        # Normalize filename: remove spaces, convert to uppercase, remove common suffixes
        normalized_search = filename.upper().replace(' ', '_').replace('-', '_')
        normalized_search = re.sub(r'_ASSAY\.MD$|_TEST\.MD$|_TESTING\.MD$', '.md', normalized_search)
        normalized_search = normalized_search.replace('.MD', '.md')
        
        # Try to find matching file in Procedures
        procedures_dir = Path("./data/parsed/LabDocs/Procedures")
        for proc_file in procedures_dir.glob("*.md"):
            proc_normalized = proc_file.name.upper().replace(' ', '_').replace('-', '_')
            # Check if normalized names match (allowing for some variation)
            if normalized_search.replace('.md', '') in proc_normalized or proc_normalized.replace('.md', '') in normalized_search:
                doc_path = proc_file
                break
        
        # If still not found, check extraction files for source_document
        if (not doc_path or not doc_path.exists()) and filename:
            try:
                extractions_dir = Path("graphdb_unified/extractions")
                if extractions_dir.exists():
                    # Try to find extraction file that might reference this document
                    filename_base = filename.replace('.md', '').upper()
                    for json_file in extractions_dir.glob("*.json"):
                        try:
                            with open(json_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            source_doc = data.get("source_document", "")
                            if source_doc:
                                # Check if filename matches
                                source_name = Path(source_doc).name.upper().replace(' ', '_').replace('-', '_')
                                if filename_base in source_name or source_name.replace('.MD', '') == filename_base:
                                    # Found matching source document
                                    source_path = Path(source_doc)
                                    if not source_path.is_absolute():
                                        source_path = Path("./") / source_doc.lstrip("./")
                                    if source_path.exists():
                                        doc_path = source_path
                                        break
                        except Exception:
                            continue
            except Exception:
                pass

    if not doc_path:
        return jsonify({"error": f"Document path not resolved: {filename}"}), 404
    
    # Resolve to absolute path for better error messages
    try:
        doc_path = doc_path.resolve()
    except Exception:
        pass
    
    if not doc_path.exists():
        return jsonify({
            "error": f"Document not found: {filename}",
            "attempted_path": str(doc_path),
            "filepath_param": filepath
        }), 404

    try:
        with open(doc_path, "r", encoding='utf-8') as f:
            content = f.read()

        return jsonify({
            "filename": filename,
            "filepath": str(doc_path),
            "content": content,
            "segment": segment
        }), 200

    except Exception as e:
        return jsonify({"error": str(e), "filepath": str(doc_path)}), 500

@app.route('/kg_query', methods=['POST'])
def kg_query():
    """
    Query the knowledge graph using Neo4j and Bedrock LLM.
    
    Request body:
        {
            "query": "What instruments are used?",
            "limit": 30  # optional, default 20
        }
    
    Response:
        {
            "question": "...",
            "answer": "...",
            "entities": [...],
            "relationships": [...]
        }
    """
    global kg_graph_store, kg_llm
    
    # Initialize KG components if not already initialized
    if kg_graph_store is None or kg_llm is None:
        try:
            initialize_kg_components()
        except Exception as e:
            return jsonify({"error": f"Failed to initialize KG components: {str(e)}"}), 500
    
    data = request.json
    question = data.get('query', '').strip()
    limit = data.get('limit', 20)
    
    if not question:
        return jsonify({"error": "Query is required"}), 400
    
    try:
        # Retrieve context from graph
        context = retrieve_context_from_graph(question, kg_graph_store, limit=limit)
        
        # Query knowledge graph
        answer = query_knowledge_graph(question, kg_graph_store, kg_llm, limit=limit)
        
        # Parse relationships into structured format for graph visualization
        graph_data = {
            'nodes': [],
            'edges': []
        }
        
        # Create nodes from entities
        entity_set = set()
        for entity in context.get('entities', []):
            if entity not in entity_set:
                entity_set.add(entity)
                graph_data['nodes'].append({
                    'id': entity,
                    'label': entity,
                    'title': entity
                })
        
        # Parse relationships into edges
        for rel_str in context.get('relationships', []):
            # Parse format: "source -[rel_type]-> target"
            match = re.match(r'(.+?)\s+-\[(.+?)\]\->\s+(.+?)$', rel_str)
            if match:
                source, rel_type, target = match.groups()
                graph_data['edges'].append({
                    'source': source.strip(),
                    'target': target.strip(),
                    'type': rel_type.strip(),
                    'label': rel_type.strip()
                })
                # Add nodes if not already present
                if source.strip() not in entity_set:
                    entity_set.add(source.strip())
                    graph_data['nodes'].append({
                        'id': source.strip(),
                        'label': source.strip(),
                        'title': source.strip()
                    })
                if target.strip() not in entity_set:
                    entity_set.add(target.strip())
                    graph_data['nodes'].append({
                        'id': target.strip(),
                        'label': target.strip(),
                        'title': target.strip()
                    })
        
        # Find paths from entities to documents for each reference
        document_paths = {}
        if context.get('entities'):
            try:
                with kg_graph_store._driver.session() as session:
                    # For each potential document reference, find shortest path from query entities
                    for entity in context.get('entities', [])[:20]:  # Limit to avoid too many queries
                        # Try to find paths from this entity to SOP documents
                        # Look for entities that might be document names
                        if any(keyword in entity.lower() for keyword in ['serum', 'plasma', 'assay', 'procedure', 'test']):
                            # Find shortest path from query entities to this entity
                            entity_list = "', '".join(context.get('entities', [])[:10])
                            path_query = f"""
                            MATCH path = shortestPath((start)-[*..4]->(end))
                            WHERE start.name IN ['{entity_list}'] 
                            AND end.name = $entity_name
                            AND end.name IS NOT NULL
                            AND ALL(node IN nodes(path) WHERE node.name IS NOT NULL)
                            RETURN path
                            ORDER BY length(path)
                            LIMIT 1
                            """
                            try:
                                result = session.run(path_query, entity_name=entity)
                                record = result.single()
                                if record and record['path']:
                                    path = record['path']
                                    nodes_in_path = []
                                    for node in path.nodes:
                                        if 'name' in node and node['name']:
                                            nodes_in_path.append(node['name'])
                                    
                                    relationships_in_path = []
                                    for rel in path.relationships:
                                        rel_type = rel.type
                                        relationships_in_path.append(rel_type)
                                    
                                    if len(nodes_in_path) > 1:
                                        document_paths[entity] = {
                                            'nodes': nodes_in_path,
                                            'relationships': relationships_in_path
                                        }
                            except Exception as path_error:
                                # Skip this entity if path finding fails
                                continue
            except Exception as e:
                # If path finding fails, continue without paths
                pass
        
        return jsonify({
            'question': question,
            'answer': answer,
            'entities': context.get('entities', []),
            'relationships': context.get('relationships', []),
            'graph': graph_data,
            'document_paths': document_paths
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/kg_chat', methods=['POST'])
def kg_chat():
    """
    Chat endpoint with conversation history support.
    
    Request body:
        {
            "message": "What instruments are used?",
            "session_id": "unique_session_id",  # optional, generates new if not provided
            "limit": 30  # optional, default 20
        }
    
    Response:
        {
            "session_id": "...",
            "message": "...",
            "answer": "...",
            "entities": [...],
            "relationships": [...],
            "references": [...],  # References with segment associations
            "graph": {...},
            "document_paths": {...}
        }
    """
    global kg_graph_store, kg_llm
    
    # Initialize KG components if not already initialized
    if kg_graph_store is None or kg_llm is None:
        try:
            initialize_kg_components()
        except Exception as e:
            return jsonify({"error": f"Failed to initialize KG components: {str(e)}"}), 500
    
    data = request.json
    message = data.get('message', '').strip()
    session_id = data.get('session_id', None)
    limit = data.get('limit', 20)
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    # Generate session ID if not provided
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
    
    # Initialize or retrieve chat history for this session
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    
    chat_history = chat_sessions[session_id]
    
    try:
        # Retrieve context from graph
        context = retrieve_context_from_graph(message, kg_graph_store, limit=limit)
        
        # Query knowledge graph with chat history
        answer = query_knowledge_graph(message, kg_graph_store, kg_llm, limit=limit, chat_history=chat_history)
        
        # Update chat history
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": answer})
        
        # Keep only last 20 messages to avoid memory issues
        if len(chat_history) > 20:
            chat_history = chat_history[-20:]
            chat_sessions[session_id] = chat_history
        
        # Parse relationships into structured format for graph visualization
        graph_data = {
            'nodes': [],
            'edges': []
        }
        
        # Create nodes from entities
        entity_set = set()
        for entity in context.get('entities', []):
            if entity not in entity_set:
                entity_set.add(entity)
                graph_data['nodes'].append({
                    'id': entity,
                    'label': entity,
                    'title': entity
                })
        
        # Parse relationships into edges
        for rel_str in context.get('relationships', []):
            # Parse format: "source -[rel_type]-> target"
            match = re.match(r'(.+?)\s+-\[(.+?)\]\->\s+(.+?)$', rel_str)
            if match:
                source, rel_type, target = match.groups()
                graph_data['edges'].append({
                    'source': source.strip(),
                    'target': target.strip(),
                    'type': rel_type.strip(),
                    'label': rel_type.strip()
                })
                # Add nodes if not already present
                if source.strip() not in entity_set:
                    entity_set.add(source.strip())
                    graph_data['nodes'].append({
                        'id': source.strip(),
                        'label': source.strip(),
                        'title': source.strip()
                    })
                if target.strip() not in entity_set:
                    entity_set.add(target.strip())
                    graph_data['nodes'].append({
                        'id': target.strip(),
                        'label': target.strip(),
                        'title': target.strip()
                    })
        
        # Extract document references and associate with answer segments
        references = extract_document_references(context.get('entities', []), answer)
        
        # Check if answer indicates no information available - filter references accordingly
        answer_lower = answer.lower()
        has_no_info = any(phrase in answer_lower for phrase in [
            'not available',
            'information is not available',
            'not available in the current knowledge base',
            'not available in the knowledge base',
            'cannot be answered',
            'no information',
            'does not contain'
        ])
        
        # Only include references if we have information
        if has_no_info:
            references = []
            document_paths = {}
        else:
            # Find paths from entities to documents for each reference
            document_paths = {}
            if context.get('entities') and references:
                try:
                    with kg_graph_store._driver.session() as session:
                        # For each reference, find path using the reference's title (which matches entity name)
                        for ref in references:
                            entity_name = ref.get('title', '')
                            if not entity_name:
                                continue
                            
                            # Try multiple strategies to find paths
                            # Strategy 1: Find path from query entities to this entity
                            entity_list = "', '".join(context.get('entities', [])[:10])
                            
                            # Use COALESCE to handle both name and title properties
                            # Also try to find the entity first to see if it exists
                            path_query = f"""
                            MATCH path = shortestPath((start)-[*..4]->(end))
                            WHERE COALESCE(start.name, start.title) IN ['{entity_list}'] 
                            AND (COALESCE(end.name, end.title) = $entity_name OR end.title CONTAINS $entity_name OR end.name CONTAINS $entity_name)
                            AND (COALESCE(end.name, end.title) IS NOT NULL)
                            AND ALL(node IN nodes(path) WHERE COALESCE(node.name, node.title) IS NOT NULL)
                            RETURN path
                            ORDER BY length(path)
                            LIMIT 1
                            """
                            
                            try:
                                result = session.run(path_query, entity_name=entity_name)
                                record = result.single()
                                if record and record['path']:
                                    path = record['path']
                                    nodes_in_path = []
                                    for node in path.nodes:
                                        node_name = node.get('name') or node.get('title')
                                        if node_name:
                                            nodes_in_path.append(node_name)
                                    
                                    relationships_in_path = []
                                    for rel in path.relationships:
                                        rel_type = rel.type
                                        relationships_in_path.append(rel_type)
                                    
                                    if len(nodes_in_path) > 1:
                                        document_paths[entity_name] = {
                                            'nodes': nodes_in_path,
                                            'relationships': relationships_in_path
                                        }
                                        continue
                            except Exception as path_error:
                                # Try alternative approach
                                pass
                            
                            # Strategy 2: If no path found, try to find the entity and its direct connections
                            try:
                                # Find the entity and its immediate neighbors
                                simple_query = """
                                MATCH (e)
                                WHERE COALESCE(e.name, e.title) = $entity_name
                                MATCH (e)-[r]-(connected)
                                WHERE COALESCE(connected.name, connected.title) IS NOT NULL
                                RETURN COALESCE(e.name, e.title) as entity,
                                       type(r) as rel_type,
                                       COALESCE(connected.name, connected.title) as connected_entity
                                LIMIT 5
                                """
                                result = session.run(simple_query, entity_name=entity_name)
                                records = list(result)
                                if records:
                                    # Build a simple path: query entity -> reference entity -> connected entities
                                    nodes_in_path = []
                                    relationships_in_path = []
                                    
                                    # Add first query entity if available
                                    if context.get('entities'):
                                        nodes_in_path.append(context.get('entities', [])[0])
                                    
                                    # Add the reference entity
                                    nodes_in_path.append(entity_name)
                                    
                                    # Add connected entities
                                    for record in records[:3]:
                                        connected = record.get('connected_entity')
                                        rel_type = record.get('rel_type')
                                        if connected and connected not in nodes_in_path:
                                            relationships_in_path.append(rel_type)
                                            nodes_in_path.append(connected)
                                    
                                    if len(nodes_in_path) > 1:
                                        document_paths[entity_name] = {
                                            'nodes': nodes_in_path,
                                            'relationships': relationships_in_path
                                        }
                            except Exception as simple_error:
                                # If all strategies fail, create a minimal path
                                if context.get('entities'):
                                    document_paths[entity_name] = {
                                        'nodes': [context.get('entities', [])[0], entity_name],
                                        'relationships': ['RELATED_TO']
                                    }
                except Exception as e:
                    # If path finding fails, continue without paths
                    import logging
                    logging.error(f"Path finding error: {e}")
                    pass
        
        return jsonify({
            'session_id': session_id,
            'message': message,
            'answer': answer,
            'entities': context.get('entities', []),
            'relationships': context.get('relationships', []),
            'references': references,
            'graph': graph_data,
            'document_paths': document_paths
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def extract_document_references(entities, answer):
    """
    Extract document references from entities and associate them with answer segments.
    Returns list of references with segment associations.
    """
    if not entities or not answer:
        return []
    
    # Load extraction files to map entities to actual source documents
    extraction_map = {}
    try:
        extractions_dir = Path("graphdb_unified/extractions")
        if extractions_dir.exists():
            for json_file in extractions_dir.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    source_doc = data.get("source_document", "")
                    if source_doc:
                        # Map entity titles to source documents
                        for entity_data in data.get("entities", []):
                            entity_title = entity_data.get("title", "")
                            if entity_title:
                                extraction_map[entity_title.lower()] = source_doc
                except Exception:
                    continue
    except Exception:
        pass
    
    # Extract potential document references (same logic as frontend)
    documentKeywords = ['serum', 'plasma', 'assay', 'test', 'procedure']
    references = []
    
    for entity in entities:
        entityLower = entity.lower()
        hasKeyword = any(keyword in entityLower for keyword in documentKeywords)
        looksLikeDoc = (
            bool(re.match(r'^\d', entity)) or  # Starts with number
            '_' in entity or  # Has underscores
            (len(entity) > 10 and 'instrument' not in entityLower and 'equipment' not in entityLower)
        )
        
        if hasKeyword and looksLikeDoc:
            # First, try to get actual source document from extraction files
            actual_filepath = extraction_map.get(entityLower)
            
            if actual_filepath:
                # Use the actual source document path
                doc_path = Path(actual_filepath)
                if not doc_path.is_absolute():
                    doc_path = Path("./") / actual_filepath.lstrip("./")
                filename = doc_path.name
                filepath = str(doc_path)
            else:
                # Extract filename (simplified version of frontend logic)
                filename = entity.strip()
                numberMatch = re.match(r'(\d+[-_]?\s*[A-Za-z][A-Za-z0-9\s-]*?)(?:[,;]|\s+(?:serum|plasma|blood|urine|csf|tissue|varies|testing|test))/i', filename)
                
                if numberMatch:
                    assayName = numberMatch[1].strip().upper()
                    # Normalize filename
                    if re.match(r'^\d+\s*-', assayName):
                        assayName = re.sub(r'^(\d+)\s*-\s*', r'\1-', assayName).replace(' ', '_')
                    elif re.match(r'^\d+-', assayName):
                        parts = assayName.split('-')
                        if len(parts) > 1:
                            assayName = parts[0] + '-' + parts[1].replace(' ', '_').upper()
                    else:
                        assayName = re.sub(r'[\s-]+', '_', assayName)
                    
                    filename = assayName.replace(',', '').replace(';', '').replace('_+', '_').strip()
                    
                    # Extract specimen type
                    afterMatch = filename[filename.find(numberMatch[0]) + len(numberMatch[0]):] if numberMatch else ''
                    specimenMatch = re.search(r'\b(serum|plasma|blood|urine|csf|cerebrospinal\s+fluid|tissue|varies|meconium|amniotic\s+fluid|pleural\s+fluid|pericardial\s+fluid|peritoneal\s+fluid|synovial\s+fluid|spinal\s+fluid)\b', afterMatch, re.I)
                    specimenType = ''
                    if specimenMatch:
                        specimenType = specimenMatch[1].upper().replace(' ', '_')
                        if 'CEREBROSPINAL' in specimenType:
                            specimenType = 'CSF'
                        elif 'AMNIOTIC' in specimenType:
                            specimenType = 'AMNIOTIC_FLUID'
                        elif 'PLEURAL' in specimenType:
                            specimenType = 'PLEURAL_FLUID'
                        elif 'PERICARDIAL' in specimenType:
                            specimenType = 'PERICARDIAL_FLUID'
                        elif 'PERITONEAL' in specimenType:
                            specimenType = 'PERITONEAL_FLUID'
                        elif 'SYNOVIAL' in specimenType:
                            specimenType = 'SYNOVIAL_FLUID'
                        elif 'SPINAL' in specimenType and 'CSF' not in specimenType:
                            specimenType = 'SPINAL_FLUID'
                    
                    if specimenType and specimenType not in filename:
                        filename = filename + '_' + specimenType
                
                # Clean up filename
                filename = re.sub(r'^(STANDARD_OPERATING_PROCEDURE_FOR_|SOP_|ASSAY_|PROCEDURE_|ANALYTICAL_PHASE_OF_|PHASE_OF_)', '', filename, flags=re.I)
                filename = re.sub(r'[,;]', '', filename).replace('_+', '_').replace('_TESTING$', '').replace('_TEST$', '').strip('_')
                
                if not filename.endswith('.md'):
                    filename = filename + '.md'
                
                filepath = f'./data/parsed/LabDocs/Procedures/{filename}'
            
            # Find segments in answer that mention this entity
            answer_lower = answer.lower()
            entity_lower = entity.lower()
            segments = []
            
            # Split answer into sentences and find those mentioning the entity
            sentences = re.split(r'[.!?]\s+', answer)
            for i, sentence in enumerate(sentences):
                if entity_lower in sentence.lower():
                    # Get context around the sentence (previous + current + next)
                    start_idx = max(0, i - 1)
                    end_idx = min(len(sentences), i + 2)
                    segment_text = '. '.join(sentences[start_idx:end_idx])
                    segments.append({
                        'text': segment_text,
                        'sentence_index': i,
                        'start_char': answer.find(sentence),
                        'end_char': answer.find(sentence) + len(sentence)
                    })
            
            references.append({
                'filename': filename,
                'title': entity,
                'filepath': filepath,
                'segments': segments[:3],  # Limit to 3 segments per reference
                'preview': f'Entity from knowledge graph: {entity}'
            })
    
    return references[:10]  # Limit to 10 references

@app.route('/kg_node_graph', methods=['POST'])
def get_node_graph():
    """
    Get graph data centered on a specific node or relationship.
    
    Request body:
        {
            "node_name": "Entity Name",  # For node-centered view
            "relationship_type": "REL_TYPE",  # Optional: for relationship view
            "limit": 20  # Number of connected nodes to return
        }
    """
    global kg_graph_store
    
    if kg_graph_store is None:
        try:
            initialize_kg_components()
        except Exception as e:
            return jsonify({"error": f"Failed to initialize KG components: {str(e)}"}), 500
    
    data = request.json
    node_name = data.get('node_name', '')
    relationship_type = data.get('relationship_type', None)
    limit = data.get('limit', 20)
    
    if not node_name:
        return jsonify({"error": "node_name is required"}), 400
    
    try:
        with kg_graph_store._driver.session() as session:
            graph_data = {
                'nodes': [],
                'edges': []
            }
            
            # Find the center node
            center_query = """
            MATCH (center)
            WHERE COALESCE(center.name, center.title) = $node_name
            RETURN center, labels(center) as labels
            LIMIT 1
            """
            result = session.run(center_query, node_name=node_name)
            record = result.single()
            
            if not record:
                return jsonify({"error": f"Node '{node_name}' not found"}), 404
            
            center_node = record['center']
            center_name = center_node.get('name') or center_node.get('title')
            center_labels = record['labels']
            
            # Add center node
            graph_data['nodes'].append({
                'id': center_name,
                'label': center_name,
                'title': center_name,
                'isCenter': True,
                'labels': center_labels
            })
            
            # If relationship type specified, find nodes connected via that relationship
            if relationship_type:
                rel_query = """
                MATCH (center)-[r]->(connected)
                WHERE COALESCE(center.name, center.title) = $node_name
                AND type(r) = $rel_type
                RETURN DISTINCT connected, type(r) as rel_type, labels(connected) as labels
                LIMIT $limit
                """
                result = session.run(rel_query, node_name=node_name, rel_type=relationship_type, limit=limit)
            else:
                # Get all connected nodes
                connected_query = """
                MATCH (center)-[r]-(connected)
                WHERE COALESCE(center.name, center.title) = $node_name
                RETURN DISTINCT connected, type(r) as rel_type, labels(connected) as labels, 
                       startNode(r) = center as isOutgoing
                LIMIT $limit
                """
                result = session.run(connected_query, node_name=node_name, limit=limit)
            
            node_set = {center_name}
            for record in result:
                connected_node = record['connected']
                connected_name = connected_node.get('name') or connected_node.get('title')
                rel_type = record['rel_type']
                connected_labels = record['labels']
                is_outgoing = record.get('isOutgoing', True)
                
                if connected_name and connected_name not in node_set:
                    node_set.add(connected_name)
                    graph_data['nodes'].append({
                        'id': connected_name,
                        'label': connected_name,
                        'title': connected_name,
                        'isCenter': False,
                        'labels': connected_labels
                    })
                
                # Add edge
                source = center_name if is_outgoing else connected_name
                target = connected_name if is_outgoing else center_name
                
                graph_data['edges'].append({
                    'source': source,
                    'target': target,
                    'type': rel_type,
                    'label': rel_type
                })
            
            return jsonify({
                'center_node': center_name,
                'graph': graph_data,
                'node_count': len(graph_data['nodes']),
                'edge_count': len(graph_data['edges'])
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/kg_chat/<session_id>', methods=['DELETE'])
def clear_chat_session(session_id):
    """Clear chat history for a session."""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        return jsonify({"status": "cleared"}), 200
    return jsonify({"error": "Session not found"}), 404

@app.route('/kg_suggestions', methods=['GET'])
def get_query_suggestions():
    """Get query suggestions based on the knowledge graph content."""
    try:
        # First, try to load verified questions (created from actual document review)
        project_root = Path(__file__).parent.parent.parent
        suggestions_file = project_root / "docs" / "query_suggestions.json"
        if suggestions_file.exists():
            import json
            with open(suggestions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # If it has verified questions, use those
                if data.get("metadata", {}).get("verified"):
                    return jsonify({
                        "suggestions": data.get("suggestions", []),
                        "metadata": data.get("metadata", {})
                    }), 200
        
        # Otherwise, generate on-the-fly
        if kg_graph_store is None:
            try:
                initialize_kg_components()
            except Exception as e:
                return jsonify({"error": f"Failed to initialize KG components: {str(e)}"}), 500
        
        # Import the suggestion generator
        sys.path.insert(0, str(scripts_dir))
        from generate_query_suggestions import (
            get_procedures_and_assays,
            get_instruments_and_devices,
            get_popular_relationships,
            get_entities_by_category,
            generate_query_suggestions
        )
        
        procedures = get_procedures_and_assays(kg_graph_store, limit=8)
        instruments = get_instruments_and_devices(kg_graph_store, limit=5)
        relationships = get_popular_relationships(kg_graph_store, limit=10)
        categories = get_entities_by_category(kg_graph_store)
        
        suggestions = generate_query_suggestions(procedures, instruments, relationships, categories)
        
        return jsonify({
            "suggestions": suggestions,
            "metadata": {
                "total_procedures": len(procedures),
                "total_instruments": len(instruments),
                "total_relationships": len(relationships)
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/documents', methods=['GET'])
def get_documents():
    """
    Get list of all indexed documents with metadata.
    
    Query parameters:
        - doc_type: Filter by document type ('sop', 'fda', or 'all')
        - section: Filter by section/subsection (optional)
        - search: Search in document titles/content (optional)
    
    Returns:
        {
            "documents": [
                {
                    "filename": "...",
                    "filepath": "...",
                    "document_type": "sop" | "fda",
                    "title": "...",
                    "preview": "...",
                    "sections": [...]
                }
            ],
            "total": 123,
            "filters": {...}
        }
    """
    try:
        import json
        from collections import defaultdict
        
        doc_type_filter = request.args.get('doc_type', 'all')
        section_filter = request.args.get('section', '')
        search_query = request.args.get('search', '').lower()
        
        documents = []
        
        # Load from extraction files in graphdb_unified/extractions
        extractions_dir = Path("graphdb_unified/extractions")
        if not extractions_dir.exists():
            return jsonify({
                "documents": [],
                "total": 0,
                "filters": {
                    "doc_type": doc_type_filter,
                    "section": section_filter,
                    "search": search_query
                }
            }), 200
        
        # Also check vectordb for additional metadata
        vectordb_dir = Path("./vectordb")
        vectordb_metadata = {}
        if vectordb_dir.exists():
            try:
                storage_context = StorageContext.from_defaults(persist_dir=str(vectordb_dir))
                index = load_index_from_storage(storage_context)
                for node_id in index.docstore.docs:
                    node = index.docstore.get_document(node_id)
                    if node.metadata and "filename" in node.metadata:
                        filename = node.metadata["filename"]
                        if filename not in vectordb_metadata:
                            vectordb_metadata[filename] = {
                                "filepath": node.metadata.get("filepath", ""),
                                "source": node.metadata.get("source", ""),
                                "chunks": []
                            }
                        # Extract section from text if it's a markdown heading
                        text = node.text[:500] if node.text else ""
                        vectordb_metadata[filename]["chunks"].append({
                            "text": text,
                            "chunk_id": node.metadata.get("chunk_id", 0)
                        })
            except Exception as e:
                print(f"Warning: Could not load vectordb metadata: {e}")
        
        # Process extraction files
        for json_file in extractions_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                source_doc = data.get("source_document", "")
                doc_type = data.get("document_type", "unknown")
                
                # Apply filters
                if doc_type_filter != 'all' and doc_type != doc_type_filter:
                    continue
                
                # Extract filename and path
                if source_doc:
                    doc_path = Path(source_doc)
                    filename = doc_path.name
                    # Keep the full relative path from data/parsed/LabDocs
                    # The filepath should be relative to the workspace root
                    if str(doc_path).startswith("data/parsed"):
                        filepath = str(doc_path)
                    else:
                        filepath = str(doc_path)
                else:
                    filename = json_file.stem + ".md"
                    filepath = ""
                
                # Extract title from entities
                title = filename.replace('.md', '').replace('_', ' ')
                entities = data.get("entities", [])
                if entities:
                    # Try to find SOP or FDA document entity
                    for entity in entities:
                        if entity.get("@type") in ["SOP", "FDADocument"]:
                            title = entity.get("title", title)
                            break
                
                # Extract sections from entities (ProcedureStep, etc.)
                sections = []
                section_set = set()
                for entity in entities:
                    entity_type = entity.get("@type", "")
                    entity_title = entity.get("title", "")
                    if entity_type in ["ProcedureStep", "Section", "Subsection"]:
                        if entity_title and entity_title not in section_set:
                            section_set.add(entity_title)
                            sections.append({
                                "title": entity_title,
                                "type": entity_type
                            })
                
                # Get preview from first entity or file
                preview = ""
                content = None  # Will load content if filepath exists
                if entities:
                    first_entity = entities[0]
                    relations = first_entity.get("relations", [])
                    if relations:
                        preview = relations[0].get("source_text", "")[:200]
                
                # If no preview, try to get from vectordb
                if not preview and filename in vectordb_metadata:
                    chunks = vectordb_metadata[filename].get("chunks", [])
                    if chunks:
                        preview = chunks[0].get("text", "")[:200]
                
                # Load document content if filepath exists (for fast rendering)
                if filepath:
                    try:
                        doc_file_path = Path(filepath)
                        if not doc_file_path.is_absolute():
                            clean_path = filepath.lstrip("./")
                            if clean_path.startswith("data/parsed"):
                                doc_file_path = Path("./") / clean_path
                            else:
                                doc_file_path = Path("./data/parsed/LabDocs") / clean_path
                        
                        if doc_file_path.exists():
                            with open(doc_file_path, "r", encoding='utf-8') as f:
                                content = f.read()
                    except Exception as content_error:
                        # If content loading fails, continue without content
                        content = None
                
                # Apply search filter
                if search_query:
                    searchable_text = f"{title} {preview}".lower()
                    if search_query not in searchable_text:
                        continue
                
                # Apply section filter
                if section_filter:
                    section_match = any(
                        section_filter.lower() in s["title"].lower() 
                        for s in sections
                    )
                    if not section_match and section_filter.lower() not in title.lower():
                        continue
                
                documents.append({
                    "filename": filename,
                    "filepath": filepath,
                    "document_type": doc_type,
                    "title": title,
                    "preview": preview,
                    "sections": sections[:10],  # Limit sections
                    "entity_count": len(entities),
                    "content": content  # Include content if available
                })
                
            except Exception as e:
                print(f"Error processing {json_file}: {e}")
                continue
        
        # Sort by document type, then by title
        documents.sort(key=lambda x: (x["document_type"], x["title"]))
        
        return jsonify({
            "documents": documents,
            "total": len(documents),
            "filters": {
                "doc_type": doc_type_filter,
                "section": section_filter,
                "search": search_query
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
