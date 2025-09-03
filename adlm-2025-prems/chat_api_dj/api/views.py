import json
import asyncio
import uuid
from typing import Dict, Any
from django.http import StreamingHttpResponse, JsonResponse
from ninja import NinjaAPI
from ollama import chat, ChatResponse

# Feature flags
FEATURE_TOOL_CALLS = True

MODEL = 'qwen3:0.6b'

SYSTEM_PROMPT = """
You are a helpful assistant running a streaming chat API that can use tools to help you answer questions.
"""

# Define a python tool
async def add_two_numbers(a: int, b: int) -> int:
    """
    Add two numbers

    Args:
        a (int): The first number as an int
        b (int): The second number as an int

    Returns:
        int: The sum of the two numbers
    """
    return a + b

TOOLS = {
    'add_two_numbers': add_two_numbers
}

# Create NinjaAPI instance
api = NinjaAPI(title="Chat API", version="1.0.0")

@api.get("/health")
async def health_check(request):
    """Health check endpoint"""
    return {"status": "healthy", "service": "chat-api"}

@api.post("/chat")
async def chat_stream_endpoint(request):
    """Streaming chat endpoint with tool calls support"""
    
    try:
        # Parse request body
        body = json.loads(request.body)
        if not body or "message" not in body:
            return JsonResponse({"error": "Missing 'message' field"}, status=400)

        message = body["message"]
        
        # Generate a unique chat request ID for this request
        chat_request_id = str(uuid.uuid4())
        
        # Prepare messages for Ollama
        messages = [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': message}
        ]
        
        def generate_response():
            # Local counter for tool calls within this request
            local_call_counter = 0
            
            try:
                response: ChatResponse = chat(
                    model=MODEL,
                    messages=messages,
                    tools=TOOLS.values(),  # Python SDK supports passing tools as functions
                    stream=True
                )
                
                for chunk in response:
                    # Prepare response data
                    reply = chunk.message.content or ""
                    yield f'reply: {json.dumps(reply)}\n'
                    
                    # Add tool calls if present
                    if chunk.message.tool_calls:
                        for call in chunk.message.tool_calls:
                            # Generate unique call ID using chat_request_id + local counter
                            local_call_counter += 1
                            call_id = f"{chat_request_id}"
                            
                            tool_call = {
                                'id': call_id,
                                'function': call.function.name,
                                'arguments': call.function.arguments
                            }
                            yield f'tool_call_started: {json.dumps(tool_call)}\n'
                            
                            # Execute tool call synchronously in generator
                            import asyncio
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                tool_response_value = loop.run_until_complete(
                                    TOOLS[call.function.name](**call.function.arguments)
                                )
                            finally:
                                loop.close()
                            
                            tool_response = {
                                'id': call_id,
                                'value': tool_response_value
                            }
                            yield f'tool_call_response: {json.dumps(tool_response)}\n'
                            
            except Exception as e:
                yield f'error: {str(e)}\n'
        
        return StreamingHttpResponse(
            generate_response(),
            content_type="text/event-stream"
        )
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
