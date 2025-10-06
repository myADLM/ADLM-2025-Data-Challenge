import os

from app.src.api.api_objects import ChatItem, QueryModel
from app.src.chat.nova_client import NovaClient
from app.src.util.open_ai_api import OpenAIAPI


def chat(
    model: QueryModel, messages: list[ChatItem], context_chunks: list[dict[str, str]]
) -> str:
    if model == QueryModel.NONE:
        return "NO CHAT MODEL SELECTED: I've attached some relevant documents to your question."

    # Check if OpenAI API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        return "OPENAI_API_KEY is not available. Please set the OPENAI_API_KEY environment variable to use GPT models."

    if model == QueryModel.GPT5_NANO:
        return _openai_chat("gpt-5", messages, context_chunks)
    if model == QueryModel.GPT5_MINI:
        return _openai_chat("gpt-5-mini", messages, context_chunks)
    if model == QueryModel.GPT5:
        return _openai_chat("gpt-5-nano", messages, context_chunks)
    if model == QueryModel.NOVA:
        return _nova_chat(messages, context_chunks)
    raise ValueError(f"Invalid chat model: {model}")


def _openai_chat(
    model: str, messages: list[ChatItem], context_chunks: list[dict[str, str]]
) -> str:
    try:
        openai_client = OpenAIAPI()

        openai_messages = []
        for msg in messages:
            openai_messages.append({"role": msg.role.value, "content": msg.text})

        response = openai_client.chat(
            messages=openai_messages,
            context_chunks=context_chunks,
            model=model,
        )

        return response
    except Exception as e:
        return f"Error querying gpt {model}: {str(e)}"


def _nova_chat(
    messages: list[ChatItem], context_chunks: list[dict[str, str]]
) -> str | None:
    try:
        nova_client = NovaClient()

        nova_messages = []
        for msg in messages:
            nova_messages.append({"role": msg.role.value, "content": msg.text})

            response = nova_client.chat(
                messages=nova_messages,
                context_chunks=context_chunks,
                model="amazon.nova-pro-v1:0",
            )

            return response
    except Exception as e:
        return f"Error calling Amazon Nova Pro: {str(e)}"
