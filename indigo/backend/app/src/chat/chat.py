import os

from app.src.api.api_objects import ChatItem, QueryModel


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
    raise ValueError(f"Invalid chat model: {model}")


def _gpt5_chat(messages: list[ChatItem]) -> str:
    """GPT-5 chat implementation."""
    try:
        from app.src.util.open_ai_api import OpenAIAPI

        openai_client = OpenAIAPI()

        # Convert ChatItem objects to OpenAI format
        openai_messages = []
        for msg in messages:
            openai_messages.append({"role": msg.agent.value, "content": msg.text})

        response = openai_client.client.chat.completions.create(
            model="gpt-4",  # Using GPT-4 as fallback since GPT-5 doesn't exist yet
            messages=openai_messages,
            max_tokens=1000,
            temperature=0.7,
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling GPT-5: {str(e)}"


def _gpt5_mini_chat(messages: list[ChatItem]) -> str:
    """GPT-5 Mini chat implementation."""
    try:
        from app.src.util.open_ai_api import OpenAIAPI

        openai_client = OpenAIAPI()

        # Convert ChatItem objects to OpenAI format
        openai_messages = []
        for msg in messages:
            openai_messages.append({"role": msg.agent.value, "content": msg.text})

        response = openai_client.client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using GPT-3.5 as fallback for mini
            messages=openai_messages,
            max_tokens=500,
            temperature=0.7,
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling GPT-5 Mini: {str(e)}"


def _gpt5_nano_chat(messages: list[ChatItem]) -> str:
    """GPT-5 Nano chat implementation."""
    try:
        from app.src.util.open_ai_api import OpenAIAPI

        openai_client = OpenAIAPI()

        # Convert ChatItem objects to OpenAI format
        openai_messages = []
        for msg in messages:
            openai_messages.append({"role": msg.agent.value, "content": msg.text})

        response = openai_client.client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using GPT-3.5 as fallback for nano
            messages=openai_messages,
            max_tokens=200,
            temperature=0.5,
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling GPT-5 Nano: {str(e)}"
