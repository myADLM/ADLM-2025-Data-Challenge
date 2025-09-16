from pydantic import BaseModel, Field, HttpUrl
from typing import List, Literal, Optional
from enum import Enum


class AgentType(str, Enum):
    """Enumeration of supported agent types."""
    USER = "user"
    ASSISTANT = "assistant"


class ChatItem(BaseModel):
    """Individual chat message item."""
    agent: AgentType = Field(..., description="The agent who sent the message")
    text: str = Field(..., min_length=1, description="The text content of the message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent": "user",
                "text": "What is the main topic of this document?"
            }
        }


class ChatRequest(BaseModel):
    """Request object for chat interactions containing a list of chat items."""
    chat_items: List[ChatItem] = Field(..., min_length=1, description="List of chat messages in conversation order")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chat_items": [
                    {
                        "agent": "user",
                        "text": "What is the main topic of this document?"
                    },
                    {
                        "agent": "assistant", 
                        "text": "I'll help you find information about the document topic."
                    }
                ]
            }
        }


class Document(BaseModel):
    """Document model containing title and download URL."""
    title: str = Field(..., min_length=1, description="The title of the document")
    url: str = Field(..., description="URL to download the document")
    ghost: str = Field(..., description="Ghost text for the document")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "FDA Cardiovascular Guidelines",
                "url": "/documents/cardiovascular-guidelines.pdf",
                "ghost": "LabDocs/FDA/Cardiovascular/guidelines.pdf"
            }
        }


class ChatResponse(BaseModel):
    """Response object for chat interactions containing chat items and relevant documents."""
    chat_items: List[ChatItem] = Field(..., description="List of chat messages in conversation order")
    documents: List[Document] = Field(default_factory=list, description="List of relevant documents found during the conversation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chat_items": [
                    {
                        "agent": "user",
                        "text": "What documents are available about cardiovascular testing?"
                    },
                    {
                        "agent": "assistant",
                        "text": "I found several relevant documents about cardiovascular testing. Here are the most relevant ones:"
                    }
                ],
                "documents": [
                    {
                        "title": "FDA Cardiovascular Guidelines",
                        "url": "/documents/cardiovascular-guidelines.pdf"
                    },
                    {
                        "title": "Clinical Chemistry Protocols",
                        "url": "/documents/clinical-chemistry-protocols.pdf"
                    }
                ]
            }
        }
