"""
API data models and objects for the document search and chat system.

This module defines Pydantic models for API requests/responses and enumerations
for supported models and search types.
"""

from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class RoleType(str, Enum):
    """Enumeration of supported role types."""

    USER = "user"
    ASSISTANT = "assistant"


class QueryModel(str, Enum):
    """Enumeration of supported query models."""

    GPT5_NANO = "gpt-5-nano"
    GPT5_MINI = "gpt-5-mini"
    GPT5 = "gpt-5"
    NOVA = "amazon.nova-pro-v1:0"
    NONE = "none"


class SearchType(str, Enum):
    """Enumeration of supported document search algorithms."""

    BM25 = "bm25"
    VECTOR_SEARCH = "vector_search"
    RANK_FUSION = "rank_fusion"


class ChatItem(BaseModel):
    """Individual chat message item."""

    role: RoleType = Field(..., description="The role who sent the message")
    text: str = Field(..., min_length=1, description="The text content of the message")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "text": "What is the main topic of this document?",
            }
        }


class ChatRequest(BaseModel):
    """Request object for chat interactions containing a list of chat items."""

    chat_items: List[ChatItem] = Field(
        ..., min_length=1, description="List of chat messages in conversation order"
    )
    query_model: QueryModel = Field(..., description="The LLM model to query.")
    search_type: SearchType = Field(..., description="Document search algorithm.")

    class Config:
        json_schema_extra = {
            "example": {
                "chat_items": [
                    {
                        "role": "user",
                        "text": "What is the main topic of this document?",
                    },
                    {
                        "role": "assistant",
                        "text": "I'll help you find information about the document topic.",
                    },
                ],
                "query_model": "gpt-5",
                "search_type": "rank_fusion",
            }
        }


class Document(BaseModel):
    """Document model containing title and download URL."""

    title: str = Field(..., min_length=1, description="The title of the document")
    url: str = Field(..., description="URL to download the document")
    ghost: str = Field(..., description="Ghost text for the document")
    matches: List[str] = Field(
        ..., description="List of matching chunks for the document"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "FDA Cardiovascular Guidelines",
                "url": "/documents/cardiovascular-guidelines.pdf",
                "ghost": "LabDocs/FDA/Cardiovascular/guidelines.pdf",
                "matches": ["cardiovascular testing ...", "fda guidelines ..."],
            }
        }


class ChatResponse(BaseModel):
    """Response object for chat interactions containing chat items and relevant documents."""

    chat_items: List[ChatItem] = Field(
        ..., description="List of chat messages in conversation order"
    )
    documents: List[Document] = Field(
        default_factory=list,
        description="List of relevant documents found during the conversation",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "chat_items": [
                    {
                        "role": "user",
                        "text": "What documents are available about cardiovascular testing?",
                    },
                    {
                        "role": "assistant",
                        "text": "I found several relevant documents about cardiovascular testing. Here are the most relevant ones:",
                    },
                ],
                "documents": [
                    {
                        "title": "FDA Cardiovascular Guidelines",
                        "url": "/documents/cardiovascular-guidelines.pdf",
                    },
                    {
                        "title": "Clinical Chemistry Protocols",
                        "url": "/documents/clinical-chemistry-protocols.pdf",
                    },
                ],
            }
        }
