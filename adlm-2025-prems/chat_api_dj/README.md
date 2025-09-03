Streaming chat endpoint for testing LLM agents.

It's set up now to have:
- Uses `uv` to run the project and manage dependencies,
- Asynchronous using Django and django-ninja for an API framework,
- Uses ollama as an LLM,
- Stream responses,
- Make tool calls (just one for now as a placeholder).

## Installation

1. Install dependencies:
```bash
uv sync
```

2. Run migrations (if needed):
```bash
python manage.py migrate
```

3. Start the development server:
```bash
python manage.py runserver 0.0.0.0:8000
```

# Endpoints

- GET /health
- POST /chat: Request: {message: str}, Response: Streaming events [reply, tool_call_started, tool_call_response, error]

# Usage Examples

## Health Check

```bash
curl http://localhost:8000/health
```

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
```

## Chat Message

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is three plus five?"}' \
  --no-buffer
```

```powershell
$body = @{ message = "What is three plus five?" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method POST -Body $body -ContentType "application/json"
```

Example response:
```
reply: ["<think>"]
reply: ["\n"]
reply: ["Okay"]
reply: [","]
reply: [" the"]
reply: [" user"]
reply: [" is"]
reply: [" asking"]
reply: [","]
reply: [" \""]
reply: ["What"]
reply: [" is"]
reply: [" three"]
reply: [" plus"]
reply: [" five"]
reply: ["?\""]
reply: [" So"]
reply: [" they"]
reply: [" want"]
reply: [" to"]
reply: [" add"]
reply: [" three"]
reply: [" and"]
reply: [" five"]
reply: ["."]
reply: [" Let"]
reply: [" me"]
reply: [" check"]
reply: [" the"]
reply: [" tools"]
reply: [" provided"]
reply: ["."]
reply: [" There"]
reply: ["'s"]
reply: [" a"]
reply: [" function"]
reply: [" called"]
reply: [" add"]
reply: ["_two"]
reply: ["_numbers"]
reply: [" that"]
reply: [" takes"]
reply: [" two"]
reply: [" integers"]
reply: [","]
reply: [" a"]
reply: [" and"]
reply: [" b"]
reply: ["."]
reply: [" The"]
reply: [" description"]
reply: [" says"]
reply: [" it"]
reply: [" adds"]
reply: [" two"]
reply: [" numbers"]
reply: ["."]
reply: [" So"]
reply: [" I"]
reply: [" need"]
reply: [" to"]
reply: [" call"]
reply: [" this"]
reply: [" function"]
reply: [" with"]
reply: [" a"]
reply: ["="]
reply: ["3"]
reply: [" and"]
reply: [" b"]
reply: ["="]
reply: ["5"]
reply: ["."]
reply: [" The"]
reply: [" parameters"]
reply: [" are"]
reply: [" both"]
reply: [" integers"]
reply: [","]
reply: [" which"]
reply: [" matches"]
reply: [" the"]
reply: [" user"]
reply: ["'s"]
reply: [" request"]
reply: ["."]
reply: [" I"]
reply: [" should"]
reply: [" return"]
reply: [" the"]
reply: [" tool"]
reply: [" call"]
reply: [" with"]
reply: [" those"]
reply: [" values"]
reply: [".\n"]
reply: ["</think>"]
reply: ["\n\n"]
reply: [""]
tool_call_started: {"id": 1, "function": "add_two_numbers", "arguments": {"a": 3, "b": 5}}
tool_call_response: {"id": 1, "value": 8}
reply: [""]
```

**Note**: 
- The `--no-buffer` flag is important for streaming responses to display in real-time with curl
- PowerShell's `Invoke-RestMethod` will wait for the complete response before returning, so streaming responses will be buffered
- For real-time streaming in PowerShell, you might want to use `Invoke-WebRequest` with custom handling
