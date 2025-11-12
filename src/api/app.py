import os
import sys
import re
from pathlib import Path

from flask import Flask, request, jsonify
from dotenv import load_dotenv

from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.llms.bedrock_converse import BedrockConverse

# Add scripts directory to path for KG query imports
scripts_dir = Path(__file__).parent.parent.parent / "scripts" / "kg_pipeline"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from kg_query import (
    get_graph_store,
    get_bedrock_llm as get_kg_bedrock_llm,
    query_knowledge_graph,
    retrieve_context_from_graph
)

# In-memory chat sessions (in production, use Redis or database)
chat_sessions = {}

load_dotenv()

app = Flask(__name__)

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

    if not filename:
        return jsonify({"error": "Filename is required"}), 400

    doc_path = Path("./data/parsed/LabDocs/Procedures") / filename

    if not doc_path.exists():
        return jsonify({"error": f"Document not found: {filename}"}), 404

    try:
        with open(doc_path, "r") as f:
            content = f.read()

        return jsonify({
            "filename": filename,
            "content": content,
            "segment": segment
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
                        assayName = parts[0] + '-' + parts[1].replace(' ', '_')
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
                'filepath': f'./data/parsed/LabDocs/Procedures/{filename}',
                'segments': segments[:3],  # Limit to 3 segments per reference
                'preview': f'Entity from knowledge graph: {entity}'
            })
    
    return references[:10]  # Limit to 10 references

@app.route('/kg_chat/<session_id>', methods=['DELETE'])
def clear_chat_session(session_id):
    """Clear chat history for a session."""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        return jsonify({"status": "cleared"}), 200
    return jsonify({"error": "Session not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)
