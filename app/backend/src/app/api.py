from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def index():
    return {"message": "Hello, World!"}


@app.post("/api/chat")
def chat_endpoint():
    return {"response": "This is a chat response."}
