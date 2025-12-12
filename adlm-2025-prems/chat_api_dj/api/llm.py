import base64
from typing import List, Tuple, Dict
from collections import namedtuple

from openai import OpenAI
from pydantic import BaseModel
import cohere

SYSTEM_PROMPT = """Laboratories generate vast amounts of documentation, ranging from protocols and package inserts to regulatory materials like 510K clearance documents and checklists. These critical resources require significant time and effort to navigate, presenting a challenge for efficient decision-making and compliance management.

Create a tool capable of quickly and accurately answering questions about
these types of documents using chunks we've extracted from the documents.
""".strip()

# Used to seperately yield thinking and output content
ThinkingContent = namedtuple('ThinkingContent', ['content'])
OutputContent = namedtuple('OutputContent', ['content'])

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

class OpenAILLM:
    def __init__(self, 
                 model_name: str = '', 
                 base_url: str = 'http://localhost:6379/v1', 
                 api_key: str = '',
                 timeout: int = 30,
                 ):
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.client = OpenAI(
            api_key=self.api_key, 
            base_url=self.base_url,
            timeout=self.timeout,
        )

    def embed_text(self, text: str):
        response = self.client.embeddings.create(model=self.model_name, input=text)
        embeddings = [
            d.embedding
            for d in response.data
        ]
        return embeddings

    def chat(self, 
             prompts: str | List[str] = None, 
             conversation_history: List[Dict[str, str]] = None,
             stream: bool = True, 
             system_prompt: str = SYSTEM_PROMPT,
             structured_output: BaseModel = None,
        ):
        if isinstance(prompts, str):
            prompts = [prompts]
        if stream:
            assert len(prompts) == 1, "Streaming mode only supports one prompt"
        
        response_format = None
        if structured_output:
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "structured_output",
                    "schema": structured_output.model_json_schema()
                },
            }
            print('Response format:', response_format)
        
        for prompt in prompts:
            # Build message list: system prompt, then conversation history, then current prompt
            messages = [
                {"role": "system", "content": system_prompt},
            ]
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model_name, 
                messages=messages, 
                stream=stream,
                response_format=response_format,
            )

            if stream:
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        yield OutputContent(content=chunk.choices[0].delta.content)
            else:
                yield OutputContent(content=response.choices[0].message.content)

    def rerank(self, query: str, documents: List[str]) -> List[Tuple[str, float]]:
        prefix = '<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be "yes" or "no".<|im_end|>\n<|im_start|>user\n'
        suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"

        query_template = "{prefix}<Instruct>: {instruction}\n<Query>: {query}\n"
        document_template = "<Document>: {doc}{suffix}"

        instruction = (
            "Given a web search query, retrieve relevant passages that answer the query"
        )
        query = query_template.format(prefix=prefix, instruction=instruction, query=query)
        documents = [document_template.format(doc=doc, suffix=suffix) for doc in documents]

        cohere_client = cohere.ClientV2(
            base_url="http://localhost:6381",
            api_key="some_fake_key"
        )
        rerank_results = cohere_client.rerank(
            model="Qwen/Qwen3-Reranker-0.6B",
            query=query,
            documents=documents
        )
        results = rerank_results.results
        scores = [result.relevance_score for result in results]
        return scores

    def vision(self, image_path: str, prompt: str, system_prompt: str = SYSTEM_PROMPT):
        base64_image = encode_image(image_path)
        chat_response = self.client.chat.completions.create(
            # This one doesn't use self.model_name right now since it's very specific, but it could
            model="Qwen/Qwen3-VL-30B-A3B-Instruct",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is this an image of?"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}" }},
                    ],
                }
            ],
        )
        return chat_response.choices[0].message.content