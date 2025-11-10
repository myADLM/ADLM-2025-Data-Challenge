import os
from pathlib import Path

from flask import Flask, request, jsonify
from dotenv import load_dotenv

from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.bedrock_converse import BedrockConverse

load_dotenv()

app = Flask(__name__)

# Global query engine (initialized once at startup)
query_engine = None

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

    embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        trust_remote_code=True
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
