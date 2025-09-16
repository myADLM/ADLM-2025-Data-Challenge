#!/usr/bin/env python3
"""
Test script to verify ChatRequest and ChatItem models work correctly.
"""

import json
from app.src.api.request_objects import ChatRequest, ChatItem, AgentType

def test_chat_item_creation():
    """Test creating ChatItem objects."""
    print("Testing ChatItem creation...")
    
    # Test valid ChatItem
    chat_item = ChatItem(agent="user", text="Hello, world!")
    print(f"✓ Created ChatItem: {chat_item}")
    
    # Test with enum
    chat_item_enum = ChatItem(agent=AgentType.ASSISTANT, text="How can I help you?")
    print(f"✓ Created ChatItem with enum: {chat_item_enum}")
    
    # Test JSON serialization
    json_data = chat_item.model_dump()
    print(f"✓ JSON serialization: {json_data}")
    
    # Test JSON deserialization
    chat_item_from_json = ChatItem.model_validate(json_data)
    print(f"✓ JSON deserialization: {chat_item_from_json}")
    
    print()

def test_chat_request_creation():
    """Test creating ChatRequest objects."""
    print("Testing ChatRequest creation...")
    
    # Test valid ChatRequest
    chat_items = [
        ChatItem(agent="user", text="What is the main topic?"),
        ChatItem(agent="assistant", text="I'll help you find that information."),
        ChatItem(agent="user", text="Can you search the documents?")
    ]
    
    chat_request = ChatRequest(chat_items=chat_items)
    print(f"✓ Created ChatRequest with {len(chat_request.chat_items)} items")
    
    # Test JSON serialization
    json_data = chat_request.model_dump()
    print(f"✓ JSON serialization: {json.dumps(json_data, indent=2)}")
    
    # Test JSON deserialization
    chat_request_from_json = ChatRequest.model_validate(json_data)
    print(f"✓ JSON deserialization: {len(chat_request_from_json.chat_items)} items")
    
    print()

def test_validation_errors():
    """Test validation error handling."""
    print("Testing validation errors...")
    
    try:
        # Test invalid agent
        ChatItem(agent="invalid_agent", text="Hello")
        print("✗ Should have failed with invalid agent")
    except Exception as e:
        print(f"✓ Correctly caught invalid agent error: {type(e).__name__}")
    
    try:
        # Test empty text
        ChatItem(agent="user", text="")
        print("✗ Should have failed with empty text")
    except Exception as e:
        print(f"✓ Correctly caught empty text error: {type(e).__name__}")
    
    try:
        # Test empty chat_items list
        ChatRequest(chat_items=[])
        print("✗ Should have failed with empty chat_items")
    except Exception as e:
        print(f"✓ Correctly caught empty chat_items error: {type(e).__name__}")
    
    print()

def test_fastapi_compatibility():
    """Test that the models work with FastAPI JSON schema generation."""
    print("Testing FastAPI compatibility...")
    
    # Test JSON schema generation
    chat_item_schema = ChatItem.model_json_schema()
    print(f"✓ ChatItem JSON schema generated: {len(chat_item_schema)} fields")
    
    chat_request_schema = ChatRequest.model_json_schema()
    print(f"✓ ChatRequest JSON schema generated: {len(chat_request_schema)} fields")
    
    # Test example data
    example_data = {
        "chat_items": [
            {"agent": "user", "text": "What is the main topic?"},
            {"agent": "assistant", "text": "I'll help you find that information."}
        ]
    }
    
    chat_request = ChatRequest.model_validate(example_data)
    print(f"✓ Successfully validated example data: {len(chat_request.chat_items)} items")
    
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("Testing ChatRequest and ChatItem Models")
    print("=" * 60)
    print()
    
    test_chat_item_creation()
    test_chat_request_creation()
    test_validation_errors()
    test_fastapi_compatibility()
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)
