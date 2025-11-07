"""
LLM clients for AI chat interactions.
"""

import json
import logging
from typing import Protocol
from openai import OpenAI
import os

from app.src.util.aws import get_bedrock_client
from app.src.chat.chat_templates import system_instructions, user_query
from app.src.api.api_objects import ChatItem


logger = logging.getLogger("app")


class ChatClient(Protocol):
    def chat(self, messages: list[ChatItem], context_chunks: list[dict[str, str]], model: str) -> str:
        ...

class NovaClient(ChatClient):
    """Client for Amazon Nova Pro model interactions via AWS Bedrock."""
    
    def __init__(self):
        self.client = get_bedrock_client()
        self.max_message_history = 6  # Max lookback in message history
        self.max_message_size = 5_000
        self.consider_history=False

    def chat(
        self,
        messages: list[ChatItem],
        context_chunks: list[dict[str, str]],
        model: str = "amazon.nova-pro-v1:0",
    ) -> str:
        """Generate AI response using Nova Pro with document context."""
        # Nova model chat payloads must look like this:
        # {
        #   "schemaVersion": "messages-v1",
        #   "system": [
        #       {
        #           "text": system_instructions()
        #       }
        #   ],
        #   "messages": [
        #       {
        #           "role": "user" | "assistant",
        #           "content": [
        #               {
        #                   "text": ...,
        #                   "cachePoint": {"type": "default"}
        #               }
        #           ]
        #       },
        #       ...
        #   ],
        #   "inferenceConfig": {
        #       "temperature": ...,
        #       "maxTokens": ...
        #   },
        # }

        logger.info(f"Received messages: {messages}")
        
        if len(messages[-1].text) > self.max_message_size:
            return f"Sorry, the message exceeds the maximum message size. Please keep messages below \
                    {self.max_message_size} characters."

        # get the last N messages
        if self.consider_history:
            logger.info(f"Received messages: {messages[-self.max_message_history:]}")
            processed_messages = [
                {"role": ci.role, "content": [{"text": ci.text}]}
                for ci in messages[-self.max_message_history :]
            ]
        else:
            processed_messages = [
                {
                    "role": messages[-1].role,
                    "content": [{"text": messages[-1].text}],
                }
            ]
        logger.info(processed_messages)

        # Construct the contextual message
        processed_messages[-1]["content"][0][
            "text"
        ] = user_query(context_chunks, processed_messages[-1]["content"][0]["text"])

        logger.info(
            f"Chat message history size: {sum(map(lambda x: len(x['content'][0]['text']), processed_messages[:-1]))}"
        )
        logger.info(
            f"Contextual message size: {len(processed_messages[-1]['content'][0]['text'])}"
        )

        # Query the model
        payload = {
            "schemaVersion": "messages-v1",
            "system": [
                {
                    "text": system_instructions()
                }
            ],
            "messages": processed_messages,
            "inferenceConfig": {"temperature": 0.7, "maxTokens": 10000},
        }
        response = self.client.invoke_model(
            modelId=model,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload),
        )
        return json.loads(response["body"].read())["output"]["message"]["content"][0][
            "text"
        ].strip()

class GptClient(ChatClient):
    """Client for OpenAI GPT model interactions."""
    
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = OpenAI(api_key=api_key)
        self.max_message_size = 5_000
    
    def chat(self, messages: list[ChatItem], context_chunks: list[dict[str, str]], model: str) -> str:
        logger.info(f"Received message: {messages[-1].text}")
        
        if len(messages[-1].text) > self.max_message_size:
            return f"Sorry, the message exceeds the maximum message size. Please keep messages below \
                    {self.max_message_size} characters."
        
        response = self.client.responses.create(
            model=model,
            instructions=system_instructions(),
            input=user_query(context_chunks, messages[-1].text)
        )

        return response.output_text
