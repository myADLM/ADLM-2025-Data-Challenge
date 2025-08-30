from sanic import Sanic, Request, response
from sanic.response import json, text
from ollama import chat, ChatResponse
from typing import List, Dict, Any
import json as json_lib
import asyncio

# Feature flags
FEATURE_TOOL_CALLS = True

MODEL = 'qwen3:0.6b'

CALL_ID_COUNTER = 1

TOOL_CALL_ID_LOCK = asyncio.Lock()

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

# Create Sanic app
app = Sanic("chat-api")

# Health check endpoint
@app.get("/health")
async def health_check(request: Request):
    return json({"status": "healthy", "service": "chat-api"})

# Streaming chat endpoint
@app.post("/chat", stream=True)
async def chat_stream_endpoint(request: Request):
    global CALL_ID_COUNTER
    try:
        web_response = await request.respond(content_type="text/event-stream")

        # Parse request body
        body = await request.stream.read()
        body = json_lib.loads(body)
        if not body or "message" not in body:
            await web_response.send('error: Missing \'message\' field\n')
            await web_response.eof()
            return

        message = body["message"]
        
        # Prepare messages for Ollama
        messages = [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': message}
        ]
        
        try:
            response: ChatResponse = chat(
                model=MODEL,
                messages=messages,
                tools=TOOLS.values(),  # Python SDK supports passing tools as functions
                stream=True
            )
            
            for chunk in response:
                # Prepare response data
                reply = chunk.message.content or "",
                await web_response.send('reply: ' + json_lib.dumps(reply) + '\n')
                
                # Add tool calls if present
                if chunk.message.tool_calls:
                    for call in chunk.message.tool_calls:
                        async with TOOL_CALL_ID_LOCK:
                            call_id = CALL_ID_COUNTER
                            CALL_ID_COUNTER += 1
                        tool_call = {
                            'id': call_id,
                            'function': call.function.name,
                            'arguments': call.function.arguments
                        }
                        await web_response.send('tool_call_started: ' + json_lib.dumps(tool_call) + '\n')
                        tool_response_value = await TOOLS[call.function.name](**call.function.arguments)
                        tool_response = {
                            'id': call_id,
                            'value': tool_response_value
                        }
                        await web_response.send('tool_call_response: ' + json_lib.dumps(tool_response) + '\n')
            
        except Exception as e:
            await web_response.send('error: ' + str(e) + '\n')
        finally:
            await web_response.eof()
    except Exception as e:
        # Handle any other exceptions that might occur
        if 'web_response' in locals():
            await web_response.send('error: ' + str(e) + '\n')
            await web_response.eof()
        else:
            # If web_response wasn't created yet, return a simple error response
            return json('error: ' + str(e) + '\n')

# Main function for running the app
def main():
    app.run(
        host="0.0.0.0",
        port=8000,
        #debug=False,  # Production settings
        debug=True,
        access_log=True,
        workers=1
    )

if __name__ == "__main__":
    main()
