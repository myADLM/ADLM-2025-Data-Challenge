from app.src.api.api_objects import QueryModel
from app.src.api.api_objects import ChatItem


def chat(model: QueryModel, messages: list[ChatItem]) -> str:
    if model == QueryModel.NONE:
        return "NO CHAT MODEL SELECTED: I've attached some relevant documents to your question."
    if model == QueryModel.GPT5_NANO:
        return _gpt5_nano_chat(messages)
    if model == QueryModel.GPT5_MINI:
        return _gpt5_mini_chat(messages)
    if model == QueryModel.GPT5:
        return _gpt5_chat(messages)
    raise ValueError(f"Invalid chat model: {model}")
