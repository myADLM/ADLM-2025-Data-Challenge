from app.src.api.api_objects import ChatItem

class NovaClient:
    def __init__(self):
        raise NotImplemented("Nova Client is not implemented")
    
    def chat(messages: list[ChatItem], context_chunks: list[dict[str, str]], model="amazon-nova-pro:v1"):
        raise NotImplemented()