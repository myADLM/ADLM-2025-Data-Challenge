#!/usr/bin/env python3
"""
Test script to verify ChatResponse and Document models work correctly.
"""

import json
from app.src.api.api_objects import ChatResponse, Document, ChatItem, AgentType

def test_document_creation():
    """Test creating Document objects."""
    print("Testing Document creation...")
    
    # Test valid Document
    document = Document(title="Test Document", url="/documents/test.pdf")
    print(f"✓ Created Document: {document}")
    
    # Test JSON serialization
    json_data = document.model_dump()
    print(f"✓ JSON serialization: {json_data}")
    
    # Test JSON deserialization
    document_from_json = Document.model_validate(json_data)
    print(f"✓ JSON deserialization: {document_from_json}")
    
    print()

def test_chat_response_creation():
    """Test creating ChatResponse objects."""
    print("Testing ChatResponse creation...")
    
    # Test valid ChatResponse
    chat_items = [
        ChatItem(agent="user", text="What documents are available?"),
        ChatItem(agent="assistant", text="Here are the available documents:")
    ]
    
    documents = [
        Document(title="Document 1", url="/documents/doc1.pdf"),
        Document(title="Document 2", url="/documents/doc2.pdf")
    ]
    
    chat_response = ChatResponse(chat_items=chat_items, documents=documents)
    print(f"✓ Created ChatResponse with {len(chat_response.chat_items)} chat items and {len(chat_response.documents)} documents")
    
    # Test JSON serialization
    json_data = chat_response.model_dump()
    print(f"✓ JSON serialization: {json.dumps(json_data, indent=2)}")
    
    # Test JSON deserialization
    chat_response_from_json = ChatResponse.model_validate(json_data)
    print(f"✓ JSON deserialization: {len(chat_response_from_json.chat_items)} chat items, {len(chat_response_from_json.documents)} documents")
    
    print()

def test_empty_documents():
    """Test ChatResponse with empty documents list."""
    print("Testing ChatResponse with empty documents...")
    
    chat_items = [ChatItem(agent="user", text="Hello")]
    chat_response = ChatResponse(chat_items=chat_items)
    
    print(f"✓ Created ChatResponse with empty documents: {len(chat_response.documents)} documents")
    print(f"✓ Documents field defaults to empty list: {chat_response.documents == []}")
    
    print()

def test_validation_errors():
    """Test validation error handling."""
    print("Testing validation errors...")
    
    try:
        # Test empty title
        Document(title="", url="/documents/test.pdf")
        print("✗ Should have failed with empty title")
    except Exception as e:
        print(f"✓ Correctly caught empty title error: {type(e).__name__}")
    
    try:
        # Test missing URL
        Document(title="Test Document")
        print("✗ Should have failed with missing URL")
    except Exception as e:
        print(f"✓ Correctly caught missing URL error: {type(e).__name__}")
    
    print()

def test_fastapi_compatibility():
    """Test that the models work with FastAPI JSON schema generation."""
    print("Testing FastAPI compatibility...")
    
    # Test JSON schema generation
    document_schema = Document.model_json_schema()
    print(f"✓ Document JSON schema generated: {len(document_schema)} fields")
    
    chat_response_schema = ChatResponse.model_json_schema()
    print(f"✓ ChatResponse JSON schema generated: {len(chat_response_schema)} fields")
    
    # Test example data
    example_data = {
        "chat_items": [
            {"agent": "user", "text": "What documents are available?"},
            {"agent": "assistant", "text": "Here are the available documents:"}
        ],
        "documents": [
            {"title": "Test Document 1", "url": "/documents/test1.pdf"},
            {"title": "Test Document 2", "url": "/documents/test2.pdf"}
        ]
    }
    
    chat_response = ChatResponse.model_validate(example_data)
    print(f"✓ Successfully validated example data: {len(chat_response.chat_items)} chat items, {len(chat_response.documents)} documents")
    
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("Testing ChatResponse and Document Models")
    print("=" * 60)
    print()
    
    test_document_creation()
    test_chat_response_creation()
    test_empty_documents()
    test_validation_errors()
    test_fastapi_compatibility()
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)
