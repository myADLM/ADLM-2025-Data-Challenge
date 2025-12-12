#!/usr/bin/env python3
"""
Flask SOP Query Application
============================

A web interface for querying Standard Operating Procedures (SOPs) and FDA documents using LLM-enhanced responses.

Features:
- Choice between SOPQuery and FDAQuery systems
- Direct query processing without file management
- Enhanced LLM-powered responses
- Configurable port and external access
- Static file serving from www/ directory
- Production-ready with Gunicorn support

Usage:
    python app.py [--port 5000] [--host 0.0.0.0]
    
Then navigate to: http://localhost:5000 (or your configured host/port)
"""

import os
import sys
import json
import logging
import argparse
import requests
from pathlib import Path
from typing import List, Dict, Any

from flask import Flask, render_template, request, jsonify, session, send_from_directory

# Add parent yjacobs modules to path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
yjacobs_dir = parent_dir / 'yjacobs'
modules_dir = yjacobs_dir / 'modules'

sys.path.insert(0, str(yjacobs_dir))
sys.path.insert(0, str(modules_dir))

# Import SOPQuery and FDAQuery classes (after parent_dir is defined)
sys.path.insert(0, str(parent_dir / 'query'))
from SOPQuery import SOPQuery
from FDAQuery import FDAQuery

# Configure logging
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Create logs directory
logs_dir = current_dir / 'logs'
logs_dir.mkdir(exist_ok=True)

# Create timestamp for log filename
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = logs_dir / f'flask_app_{timestamp}.log'

# Configure logging with both file and console handlers
# Create handlers with proper encoding
file_handler = RotatingFileHandler(
    str(log_file),
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'  # Handle Unicode characters properly
)
console_handler = logging.StreamHandler()

# Set formatting
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger(__name__)

def safe_log_message(message):
    """Sanitize log messages to avoid Unicode encoding issues"""
    try:
        return message.encode('ascii', 'ignore').decode('ascii')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return repr(message)

logger.info(f"Flask Query Application starting - logs written to {log_file}")

# Create Flask app with custom template and static folders
app = Flask(__name__, 
           template_folder='templates',
           static_folder='www')
app.secret_key = 'query_app_secret_key_2024'  # Change this in production

# Global variables for query systems
sop_query_system = None
fda_query_system = None
sop_documents = None
fda_documents = None

def load_sop_documents():
    """Load SOP documents from the LabDocs directory"""
    global sop_documents
    
    try:
        logger.info("Loading SOP documents...")
        sop_dir = parent_dir / 'LabDocs' / 'es1' / 'sop'
        sops = []
        i = 0
        
        if not sop_dir.exists():
            logger.error(f"SOP directory not found: {sop_dir}")
            return []
            
        for f in sop_dir.glob('*.json'):
            try:
                json_content = f.read_text(encoding='utf-8')
                sops.append((i, f.name, json_content))
                i += 1
            except UnicodeDecodeError as e:
                logger.warning(f"Unicode error reading {f.name}: {e}")
                try:
                    json_content = f.read_text(encoding='latin-1')
                    sops.append((i, f.name, json_content))
                    i += 1
                except Exception as e2:
                    logger.error(f"Failed to read {f.name} with fallback encoding: {e2}")
                    continue
        
        logger.info(f"Successfully loaded {len(sops)} SOP documents")
        sop_documents = sops
        return sops
        
    except Exception as e:
        logger.error(f"Error loading SOP documents: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def load_fda_documents():
    """Load FDA documents from the LabDocs directory"""
    global fda_documents
    
    try:
        logger.info("Loading FDA documents...")
        fda_dir = parent_dir / 'LabDocs' / 'es1' / 'fda_summary'
        fdas = []
        i = 0
        
        if not fda_dir.exists():
            logger.error(f"FDA directory not found: {fda_dir}")
            return []
            
        # Recursively search through all subdirectories for JSON files
        for f in fda_dir.rglob('*.json'):
            try:
                # Parse the full JSON file with explicit UTF-8 encoding
                full_json = json.loads(f.read_text(encoding='utf-8'))
                
                # Extract only the Document Summary
                document_summary = full_json.get('Document Summary', 'No document summary available')
                
                # Create minimal JSON object with just the summary
                minimal_json = {
                    "Document Summary": document_summary
                }
                
                # Convert back to JSON string
                json_content = json.dumps(minimal_json, indent=2, ensure_ascii=False)
                fdas.append((i, f.name, json_content))
                i += 1
                
            except UnicodeDecodeError as e:
                logger.warning(f"Unicode error reading {f.name}: {e}")
                continue
            except json.JSONDecodeError as e:
                logger.warning(f"Skipping invalid JSON file {f.name}: {e}")
                continue
            except Exception as e:
                logger.warning(f"Error processing file {f.name}: {e}")
                continue
        
        logger.info(f"Successfully loaded {len(fdas)} FDA documents (Document Summary only)")
        fda_documents = fdas
        return fdas
        
    except Exception as e:
        logger.error(f"Error loading FDA documents: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def initialize_query_systems():
    """Initialize the SOPQuery and FDAQuery systems"""
    global sop_query_system, fda_query_system
    
    try:
        # Load documents first
        logger.info("Loading documents...")
        load_sop_documents()
        load_fda_documents()
        
        logger.info("Initializing SOPQuery system...")
        sop_query_system = SOPQuery(debug=5)  # Remove hardcoded model
        logger.info("SOPQuery system initialized successfully")
        
        logger.info("Initializing FDAQuery system...")
        fda_query_system = FDAQuery(debug=1)  # Remove hardcoded model
        logger.info("FDAQuery system initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Error initializing query systems: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def handle_general_questions(question: str) -> str:
    """Handle general questions, greetings, and non-query related questions with polite responses"""
    import re
    question_lower = question.lower().strip()
    
    # Greetings and pleasantries (match whole words only)
    greetings = ['hello', 'hi', 'good morning', 'good afternoon', 'good evening', 'hey', 'howdy']
    if any(re.search(r'\b' + re.escape(greeting) + r'\b', question_lower) for greeting in greetings):
        return ("Hello! 👋 Welcome to the Laboratory Query System. I'm here to help you find information from "
                "Standard Operating Procedures (SOPs) and FDA documents. You can ask me about:\n\n"
                "**SOP Queries:**\n"
                "• Laboratory protocols and procedures\n"
                "• Safety measures and guidelines\n"
                "• Equipment usage instructions\n"
                "• Sample preparation methods\n"
                "• Quality control procedures\n\n"
                "**FDA Queries:**\n"
                "• FDA 510(k) clearances and submissions\n"
                "• Medical device approvals\n"
                "• Regulatory requirements\n"
                "• Device specifications and indications\n\n"
                "What would you like to know today?")
    
    # Thank you messages (match whole words only)
    thanks = ['thank you', 'thanks', 'thx', 'appreciate']
    if any(re.search(r'\b' + re.escape(thank) + r'\b', question_lower) for thank in thanks):
        return ("You're very welcome! 😊 I'm glad I could help you find the information you needed. "
                "Feel free to ask if you have any more questions about SOPs or FDA documents!")
    
    # General questions about the system
    system_questions = ['what can you do', 'what do you do', 'how do you work', 'what are you', 'who are you']
    if any(sys_q in question_lower for sys_q in system_questions):
        return ("I'm an AI assistant specialized in laboratory documentation analysis. I can help you with:\n\n"
                "🔬 **SOP Analysis**: Standard Operating Procedures, laboratory protocols, safety guidelines, "
                "equipment instructions, quality control procedures, and troubleshooting steps\n\n"
                "📋 **FDA Document Analysis**: 510(k) submissions, medical device clearances, regulatory "
                "requirements, device specifications, and compliance information\n\n"
                "Just select either 'SOP Query' or 'FDA Query' and ask your question!")
    
    # Help requests (match whole words only)
    help_words = ['help', 'assistance', 'support']
    if any(re.search(r'\b' + re.escape(help_word) + r'\b', question_lower) for help_word in help_words) and len(question_lower.split()) <= 5:
        return ("I'm here to help! 🤝 Choose your query type:\n\n"
                "**SOP Query Examples:**\n"
                "• \"How do I prepare samples for blood glucose testing?\"\n"
                "• \"What are the safety procedures for handling hazardous chemicals?\"\n"
                "• \"What's the calibration procedure for the pH meter?\"\n\n"
                "**FDA Query Examples:**\n"
                "• \"What FDA clearances exist for glucose meters?\"\n"
                "• \"Show me 510(k) submissions for cardiac devices\"\n"
                "• \"What are the regulatory requirements for point-of-care testing?\"\n\n"
                "Select your query type and ask away!")
    
    # Return None if this seems like a legitimate query
    return None

@app.route('/')
def index():
    """Main page with query system selection"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files from www directory"""
    return send_from_directory('www', filename)

@app.route('/initialize_systems', methods=['POST'])
def initialize_systems():
    """Initialize the query systems"""
    try:
        if initialize_query_systems():
            return jsonify({
                'success': True,
                'message': 'Query systems initialized successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to initialize query systems'
            })
    except Exception as e:
        logger.error(f"Error in initialize_systems: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/query', methods=['POST'])
def query():
    """Process a query using either SOPQuery or FDAQuery"""
    try:
        # Auto-initialize systems if not already initialized (for multi-worker compatibility)
        if not sop_query_system or not fda_query_system or not sop_documents:
            logger.info("Auto-initializing query systems for this worker...")
            if not initialize_query_systems():
                return jsonify({'success': False, 'error': 'Failed to initialize query systems automatically.'})
        
        question = request.json.get('question', '').strip()
        query_type = request.json.get('query_type', 'sop').lower()
        show_debug = request.json.get('show_debug', False)
        clear_history = request.json.get('clear_history', False)
        
        if not question:
            return jsonify({'success': False, 'error': 'Please enter a question'})
        
        # Get or initialize conversation history
        if 'conversation_history' not in session or clear_history:
            session['conversation_history'] = []
        
        conversation_history = session['conversation_history']
        
        logger.info(f"Processing {query_type.upper()} query: {question[:50]}... (History: {len(conversation_history)} turns)")
        
        # Check if this is a greeting or general question
        polite_response = handle_general_questions(question)
        if polite_response:
            conversation_history.append({
                'question': question,
                'answer': polite_response,
                'query_type': 'general',
                'timestamp': int(__import__('time').time())
            })
            session['conversation_history'] = conversation_history
            session.modified = True
            
            return jsonify({
                'success': True,
                'response': polite_response,
                'system_used': 'Courtesy Response',
                'debug_info': None,
                'conversation_length': len(conversation_history)
            })
        
        # Process the query based on type
        if query_type == 'sop':
            try:
                logger.info("Using SOPQuery system")
                
                # Check if SOP documents are loaded
                if not sop_documents:
                    return jsonify({'success': False, 'error': 'SOP documents not loaded. Please reinitialize systems.'})
                
                # Pass the loaded SOP documents to the query system
                response, history = sop_query_system.ask_sop(
                    question,
                    sop_documents,  # Pass the loaded SOP documents
                    history=None  # Don't pass Flask session history
                )
                
                system_used = f'SOPQuery System ({len(sop_documents)} Standard Operating Procedures)'
                
            except Exception as e:
                logger.error(f"Error in SOPQuery system: {e}")
                return jsonify({'success': False, 'error': f'SOPQuery system error: {str(e)}'})
                
        elif query_type == 'fda':
            try:
                logger.info("Using FDAQuery system")
                
                # Check if FDA documents are loaded
                if not fda_documents:
                    # Try to load FDA documents and report any errors
                    try:
                        load_fda_documents()
                        if not fda_documents:
                            return jsonify({'success': False, 'error': 'FDA documents directory not found or contains no valid JSON files.'})
                    except Exception as load_error:
                        return jsonify({'success': False, 'error': f'Failed to load FDA documents: {str(load_error)}'})
                
                # Pass the loaded FDA documents to the query system
                response, history = fda_query_system.ask_fda(
                    question,
                    fda_documents,  # Pass the loaded FDA documents
                    history=None  # Don't pass Flask session history
                )
                
                system_used = f'FDAQuery System ({len(fda_documents)} FDA 510(k) Documents)'
                
            except Exception as e:
                logger.error(f"Error in FDAQuery system: {e}")
                return jsonify({'success': False, 'error': f'FDAQuery system error: {str(e)}'})
        else:
            return jsonify({'success': False, 'error': 'Invalid query type. Use "sop" or "fda".'})
        
        # Store this exchange in conversation history
        conversation_history.append({
            'question': question,
            'answer': response,
            'query_type': query_type,
            'timestamp': int(__import__('time').time())
        })
        
        # Keep only last 10 exchanges to prevent session from getting too large
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
        
        session['conversation_history'] = conversation_history
        session.modified = True
        
        debug_info = None
        if show_debug and history:
            debug_info = {
                'query_steps': len(history),
                'processing_steps': [f"Step {i+1}: {type(step).__name__ if hasattr(step, '__class__') else str(step)[:100]}" for i, step in enumerate(history[:5])],
                'system_type': f'{query_type.upper()}Query with multi-step LLM processing'
            }
        
        return jsonify({
            'success': True,
            'response': response,
            'system_used': system_used,
            'debug_info': debug_info,
            'conversation_length': len(conversation_history)
        })
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)})

@app.route('/status')
def status():
    """Get current system status"""
    import os
    return jsonify({
        'systems_initialized': sop_query_system is not None and fda_query_system is not None,
        'sop_query_ready': sop_query_system is not None,
        'fda_query_ready': fda_query_system is not None,
        'sop_documents_loaded': len(sop_documents) if sop_documents else 0,
        'fda_documents_loaded': len(fda_documents) if fda_documents else 0,
        'conversation_length': len(session.get('conversation_history', [])),
        'worker_pid': os.getpid(),
        'session_id': session.get('_id', 'session-active')
    })

@app.route('/conversation_history', methods=['GET'])
def get_conversation_history():
    """Get the current conversation history"""
    history = session.get('conversation_history', [])
    return jsonify({
        'success': True,
        'history': history,
        'length': len(history)
    })

@app.route('/clear_conversation', methods=['POST'])
def clear_conversation():
    """Clear the conversation history"""
    session['conversation_history'] = []
    session.modified = True
    return jsonify({
        'success': True,
        'message': 'Conversation history cleared'
    })

@app.route('/compare_query', methods=['POST'])
def compare_query():
    """Process a query with both SOP and FDA systems for comparison"""
    try:
        # Auto-initialize systems if not already initialized (for multi-worker compatibility)
        if not sop_query_system or not fda_query_system or not sop_documents:
            logger.info("Auto-initializing query systems for comparison...")
            if not initialize_query_systems():
                return jsonify({'success': False, 'error': 'Failed to initialize query systems automatically.'})
        
        question = request.json.get('question', '').strip()
        show_debug = request.json.get('show_debug', False)
        
        if not question:
            return jsonify({'success': False, 'error': 'Please enter a question'})
        
        logger.info(f"Processing comparison query: {question[:50]}...")
        
        # Check if this is a greeting or general question
        polite_response = handle_general_questions(question)
        if polite_response:
            return jsonify({
                'success': True,
                'sop': {
                    'response': polite_response,
                    'system_used': 'Courtesy Response'
                },
                'fda': {
                    'response': polite_response,
                    'system_used': 'Courtesy Response'
                },
                'debug_info': None
            })
        
        sop_response = "SOPQuery system not available"
        fda_response = "FDAQuery system not available"
        sop_system_used = "Not Available"
        fda_system_used = "Not Available"
        
        # Get SOPQuery response
        if sop_query_system and sop_documents:
            try:
                sop_response, _ = sop_query_system.ask_sop(
                    question,
                    sop_documents,
                    history=None
                )
                sop_system_used = 'SOPQuery System'
            except Exception as e:
                sop_response = f"SOPQuery error: {str(e)}"
                sop_system_used = "SOPQuery Error"
                logger.error(f"SOPQuery error in comparison: {e}")
        else:
            sop_response = "SOPQuery system or documents not available"
            sop_system_used = "Not Available"
        
        # Get FDAQuery response
        if fda_query_system and fda_documents:
            try:
                fda_response, _ = fda_query_system.ask_fda(
                    question,
                    fda_documents,
                    history=None
                )
                fda_system_used = 'FDAQuery System'
            except Exception as e:
                fda_response = f"FDAQuery error: {str(e)}"
                fda_system_used = "FDAQuery Error"
                logger.error(f"FDAQuery error in comparison: {e}")
        else:
            fda_response = "FDAQuery system or documents not available"
            fda_system_used = "Not Available"
        
        # Prepare debug information if requested
        debug_info = None
        if show_debug:
            debug_info = {
                'sop_query_available': sop_query_system is not None,
                'fda_query_available': fda_query_system is not None,
                'comparison_mode': True
            }
        
        return jsonify({
            'success': True,
            'sop': {
                'response': sop_response,
                'system_used': sop_system_used
            },
            'fda': {
                'response': fda_response,
                'system_used': fda_system_used
            },
            'debug_info': debug_info
        })
        
    except Exception as e:
        logger.error(f"Error processing comparison query: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ...existing code...

if __name__ == '__main__':
    # Parse command line arguments for development server
    parser = argparse.ArgumentParser(description='Flask Laboratory Query Application')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0 for external access)')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    # Suppress Flask dev server warnings
    import warnings
    warnings.filterwarnings("ignore", message=".*WERKZEUG_RUN_MAIN.*")
    
    print("🚀 Starting Flask Laboratory Query Application (Development Server)...")
    print(f"🌐 Host: {args.host}")
    print(f"🔌 Port: {args.port}")
    print("⚠️  For production, use: ./start_gunicorn.sh or ./service.sh start")
    print(f"📱 Navigate to: http://{args.host}:{args.port}")
    
    print("\n💡 Features:")
    print("   • SOPQuery: Laboratory Standard Operating Procedures")
    print("   • FDAQuery: FDA 510(k) submissions and medical device documentation")
    print("   • Multi-step LLM processing for comprehensive answers")
    print("   • Conversation history and context awareness")
    print("   • Debug mode to see query processing steps")
    print("   • Comparison mode to query both systems simultaneously")
    
    # Run the development server (HTTP only)
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
