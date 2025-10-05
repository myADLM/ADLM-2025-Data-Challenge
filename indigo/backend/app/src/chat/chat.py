import os

from app.src.api.api_objects import ChatItem, QueryModel
from app.src.util.open_ai_api import OpenAIAPI
from app.src.util.bedrock import query_model


def chat(model: QueryModel, messages: list[ChatItem]) -> str:
    if model == QueryModel.NONE:
        return "NO CHAT MODEL SELECTED: I've attached some relevant documents to your question."

    # Check if OpenAI API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        return "OPENAI_API_KEY is not available. Please set the OPENAI_API_KEY environment variable to use GPT models."

    if model == QueryModel.GPT5_NANO:
        return _gpt5_nano_chat(messages)
    if model == QueryModel.GPT5_MINI:
        return _gpt5_mini_chat(messages)
    if model == QueryModel.GPT5:
        return _gpt5_chat(messages)
    if model == QueryModel.NOVA:
        return _nova_chat(messages)
    raise ValueError(f"Invalid chat model: {model}")


def _gpt5_chat(messages: list[ChatItem]) -> str:
    """GPT-5 chat implementation."""
    try:
        openai_client = OpenAIAPI()

        # Convert ChatItem objects to OpenAI format
        openai_messages = []
        for msg in messages:
            openai_messages.append({"role": msg.agent.value, "content": msg.text})

        response = openai_client.chat(
            model="gpt-5", 
            messages=openai_messages,
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling GPT-5: {str(e)}"


def _gpt5_mini_chat(messages: list[ChatItem]) -> str:
    """GPT-5 Mini chat implementation."""
    try:
        openai_client = OpenAIAPI()

        # Convert ChatItem objects to OpenAI format
        openai_messages = []
        for msg in messages:
            openai_messages.append({"role": msg.agent.value, "content": msg.text})

        response = openai_client.chat(
            model="gpt-5-mini",
            messages=openai_messages,
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling GPT-5 Mini: {str(e)}"


def _gpt5_nano_chat(messages: list[ChatItem]) -> str:
    """GPT-5 Nano chat implementation."""
    try:
        openai_client = OpenAIAPI()

        # Convert ChatItem objects to OpenAI format
        openai_messages = []
        for msg in messages:
            openai_messages.append({"role": msg.agent.value, "content": msg.text})

        response = openai_client.client.chat.completions.create(
            model="gpt-5-nano",
            messages=openai_messages,
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling GPT-5 Nano: {str(e)}"
    
def _nova_chat(messages: list[ChatItem]) -> str:
    try:
        nova_messages = []
        for msg in messages:
            nova_messages.append({"role": msg.agent.value, "content": msg.text})

            # TODO: make amazon nova chat work

    except Exception as e:
        return f"Error calling Amazon Nova Pro: {str(e)}"
        

