import json
import logging

from app.src.util.aws import get_bedrock_client


class NovaClient:
    def __init__(self):
        self.client = get_bedrock_client()
        self.max_message_history = 6 # Max lookback in message history
        self.max_context_size = 25_000 # Max characters in the context chunks
        self.max_message_size = 5_000
    
    def chat(self,
             messages: list[dict],
             context_chunks: list[dict[str, str]],
             model: str="amazon.nova-pro-v1:0",
             consider_history=True
        ) -> str:
        logger = logging.getLogger("app")

        logger.info(f"Received messages: {messages}")
        if len(messages[-1]["content"]) > self.max_message_size:
            return f"Sorry, the message exceeds the maximum message size. Please keep messages below \
                    {self.max_message_size} characters."

        # get the last N messages
        if consider_history:
            logger.info(f"Received messages: {messages[-self.max_message_history:]}")
            processed_messages = [
                {
                    "role": ci["role"],
                    "content": [{"text": ci["content"]}]
                }
                for ci in messages[-self.max_message_history:]
            ]
        else:
            processed_messages = [
                {
                    "role": messages[-1]["role"],
                    "content": [{"text": messages[-1]["content"]}]
                }
            ]
        logger.info(processed_messages)

        # Construct the context
        context = "\n\n".join([
            f"""
            Source file: {record["file_path"]}
            Chunk: {record["contextual_chunk"]}            
            """
            for record
            in sorted(context_chunks, key=lambda d: d["file_path"])
        ])
        logger.info(context)

        # Construct the contextual message
        processed_messages[-1]["content"][0]["text"] = f"""
        DOCUMENT CHUNKS:
        {context}
        
        USER QUERY:
        {processed_messages[-1]["content"][0]["text"]}
        """

        logger.info(f"Chat message history size: {sum(map(lambda x: len(x['content'][0]['text']), processed_messages[:-1]))}")
        logger.info(f"Contextual message size: {len(processed_messages[-1]['content'][0]['text'])}")

        # Query the model
        payload = {
            "schemaVersion": "messages-v1",
            "system": [
                {
                    "text": """
                    You are a helpful AI agent working with a corpus of documents related to medical devices and process
                    documents. You will receive a question from the user and a list of partial documents that may be
                    related to the question. You should read the document chunks to reply to the question and include
                    citations from the documents.
                    """
                }
            ],
            "messages": processed_messages,
            "inferenceConfig": {"temperature": 0.7, "maxTokens": 10000},
        }
        response = self.client.invoke_model(
            modelId=model,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )
        return json.loads(response["body"].read())["output"]["message"]["content"][0]["text"].strip()
