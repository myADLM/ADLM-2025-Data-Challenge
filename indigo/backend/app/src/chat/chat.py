"""
Chat module for handling AI model interactions.

This module provides a unified interface for different AI chat models including
OpenAI GPT models and Amazon Nova Pro.
"""

import os

from app.src.api.api_objects import ChatItem, QueryModel
from app.src.chat.chat_clients import NovaClient, GptClient


def chat(
    model: QueryModel, messages: list[ChatItem], context_chunks: list[dict[str, str]]
) -> str:
    """Generate AI response using the specified model with conversation context."""
    if model == QueryModel.NONE:
        return "NO CHAT MODEL SELECTED: I've attached some relevant documents to your question."

    # Check if OpenAI API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        return "OPENAI_API_KEY is not available. Please set the OPENAI_API_KEY environment variable to use GPT models."

    if model == QueryModel.GPT5_NANO:
        return _openai_chat("gpt-5-nano", messages, context_chunks)
    if model == QueryModel.GPT5_MINI:
        return _openai_chat("gpt-5-mini", messages, context_chunks)
    if model == QueryModel.GPT5:
        return _openai_chat("gpt-5", messages, context_chunks)
    if model == QueryModel.NOVA:
        return _nova_chat(messages, context_chunks)
    raise ValueError("Invalid model")


def _openai_chat(
    model: str, messages: list[ChatItem], context_chunks: list[dict[str, str]]
) -> str:
    """Handle OpenAI GPT model chat requests."""
    try:
        openai_client = GptClient()

        response = openai_client.chat(
            messages=messages,
            context_chunks=context_chunks,
            model=model,
        )

        return response
    except Exception as e:
        return f"Error querying gpt {model}: {str(e)}"


def _nova_chat(
    messages: list[ChatItem], context_chunks: list[dict[str, str]]
) -> str:
    """Handle Amazon Nova Pro model chat requests."""
    try:
        nova_client = NovaClient()

        response = nova_client.chat(
            messages=messages,
            context_chunks=context_chunks,
            model="amazon.nova-pro-v1:0",
        )

        return response
    except Exception as e:
        return f"Error calling Amazon Nova Pro: {str(e)}"
