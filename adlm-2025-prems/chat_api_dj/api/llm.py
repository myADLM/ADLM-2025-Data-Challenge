import base64
from typing import List, Tuple
from collections import namedtuple
from threading import Thread

import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel, TextIteratorStreamer
import ollama
from openai import OpenAI

# TODO improve the prompt for use as an FDA labdocs agent
SYSTEM_PROMPT = (
    "You are a helpful assistant that helps to answer questions "
    "about FDA letters and review documents, as well as specialized "
    "standard operating procedures for a lab. We'll provide you context "
    "of the documents and your task is to answer the question based on the context."
)

# Used to seperately yield thinking and output content
ThinkingContent = namedtuple('ThinkingContent', ['content'])
OutputContent = namedtuple('OutputContent', ['content'])

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def qwen_rerank_format_instruction(instruction, query, doc):
    output = "<Instruct>: {instruction}\n<Query>: {query}\n<Document>: {doc}".format(instruction=instruction,query=query, doc=doc)
    return output


class QwenLLM:
    embedding_model_name: str = "Qwen/Qwen3-Embedding-0.6B"
    chat_model_name: str = "Qwen/Qwen3-0.6B"
    rerank_model_name: str = "Qwen/Qwen3-Reranker-0.6B"

    def __init__(self, device: str = 'cuda:3'):
        self.device = device
        self.embedding_model = None
        self.chat_tokenizer = None
        self.chat_model = None
        self.rerank_tokenizer = None
        self.rerank_model = None
        self.rerank_token_false_id = None
        self.rerank_token_true_id = None
        self.rerank_max_length = None
        self.rerank_prefix_tokens = None
        self.rerank_suffix_tokens = None
        self.initialized = False

    def _llm_initialize(self):
        """
        Setup the heavy ML models that will occupy GPU memory. This is in an initializer
        method so we don't slow down manage.py commands or other operations that don't need the LLM.
        """
        print('Initializing QwenLLM on device:', self.device)
        self.embedding_model = SentenceTransformer(
            self.embedding_model_name, 
            device=self.device,
            model_kwargs={
                "device_map": self.device,
                "attn_implementation": "flash_attention_2",
                "dtype": torch.bfloat16
            }
        ).eval()
        self.chat_tokenizer = AutoTokenizer.from_pretrained(
            self.chat_model_name
        )
        self.chat_model = AutoModelForCausalLM.from_pretrained(
            self.chat_model_name,
            device_map=self.device,
            dtype=torch.bfloat16,
            attn_implementation="flash_attention_2"
        ).eval()
        self.rerank_tokenizer = AutoTokenizer.from_pretrained(
            self.rerank_model_name, 
            padding_side='left'
        )
        self.rerank_model = AutoModelForCausalLM.from_pretrained(
            self.rerank_model_name,
            device_map=self.device,
            dtype=torch.bfloat16,
            attn_implementation="flash_attention_2"
        ).eval()

        self.rerank_token_false_id = self.rerank_tokenizer.convert_tokens_to_ids("no")
        self.rerank_token_true_id = self.rerank_tokenizer.convert_tokens_to_ids("yes")
        self.rerank_max_length = 8192

        rerank_prefix = "<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\".<|im_end|>\n<|im_start|>user\n"
        rerank_suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
        self.rerank_prefix_tokens = self.rerank_tokenizer.encode(rerank_prefix, add_special_tokens=False)
        self.rerank_suffix_tokens = self.rerank_tokenizer.encode(rerank_suffix, add_special_tokens=False)

        self.initialized = True

        print('QwenLLM initialized on device:', self.device)

    @torch.no_grad()
    def embed_text(self, text: str):
        if not self.initialized:
            self._llm_initialize()
        return self.embedding_model.encode(text)

    @torch.no_grad()
    def chat(self, prompts: str | List[str], stream: bool = True, system_prompt: str = SYSTEM_PROMPT):
        if not self.initialized:
            self._llm_initialize()
        if isinstance(prompts, str):
            prompts = [prompts]
        if stream:
            assert len(prompts) == 1, "Streaming mode only supports one prompt"
        #print('Chat prompt:', prompt)
        texts = []
        for prompt in prompts:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]
            text = self.chat_tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=True 
            )
            texts.append(text)
        #print('Texts:', texts)

        model_inputs = self.chat_tokenizer(texts, return_tensors="pt", padding=True).to(self.chat_model.device)
        #print('Model inputs')

        generate_kwargs = {
            "input_ids": model_inputs['input_ids'],
            "attention_mask": model_inputs['attention_mask'],
            "pad_token_id": self.chat_tokenizer.eos_token_id,
            "max_new_tokens": 32768,
            "temperature": 0.6,
            "top_p": 0.95,
            "top_k": 20,
            "min_p": 0,
        }

        if stream:
            streamer = TextIteratorStreamer(
                self.chat_tokenizer, 
                skip_prompt=False, 
                skip_special_tokens=True
            )
            generate_kwargs['streamer'] = streamer
            thread = Thread(
                target=self.chat_model.generate, 
                kwargs=generate_kwargs
            )
            thread.start() # now start the thread
            is_thinking = False
            for new_text in streamer:
                if new_text.startswith('system\n'):
                    continue
                if new_text == '':
                    continue

                if new_text.strip() == '<think>':
                    is_thinking = True
                    continue
                if new_text.strip() == '</think>':
                    is_thinking = False
                    continue

                if is_thinking:
                    yield ThinkingContent(content=new_text)
                else:
                    yield OutputContent(content=new_text)
            thread.join()
        else:
            generated_ids = self.chat_model.generate(**generate_kwargs)
            system_index = model_inputs['input_ids'].shape[1]
            #print('---', model_inputs['input_ids'].shape, generated_ids.shape)
            decoded = self.chat_tokenizer.batch_decode(generated_ids[:,system_index:], skip_special_tokens=True)
            #print('---Decoded:', decoded)
            for line in decoded:
                #print('---Line:', line)
                if '</think>' not in line:
                    print('---No think tag found')
                    yield ThinkingContent(content='')
                else:
                    content = line.split("</think>")[1].strip()
                    yield OutputContent(content=content)

    def _rerank_process_inputs(self, pairs):
        inputs = self.rerank_tokenizer(
            pairs, 
            padding=False, 
            truncation='longest_first',
            return_attention_mask=False, 
            max_length=self.rerank_max_length - len(self.rerank_prefix_tokens) - len(self.rerank_suffix_tokens)
        )
        for i, ele in enumerate(inputs['input_ids']):
            inputs['input_ids'][i] = self.rerank_prefix_tokens + ele + self.rerank_suffix_tokens
        inputs = self.rerank_tokenizer.pad(inputs, padding=True, return_tensors="pt", max_length=self.rerank_max_length)
        for key in inputs:
            inputs[key] = inputs[key].to(self.rerank_model.device)
        return inputs

    @torch.no_grad()
    def _rerank_compute_logits(self, inputs):
        batch_scores = self.rerank_model(**inputs).logits[:, -1, :]
        true_vector = batch_scores[:, self.rerank_token_true_id]
        false_vector = batch_scores[:, self.rerank_token_false_id]
        batch_scores = torch.stack([false_vector, true_vector], dim=1)
        batch_scores = torch.nn.functional.log_softmax(batch_scores, dim=1)
        scores = batch_scores[:, 1].exp().tolist()
        return scores

    def rerank(self, query: str, documents: List[str]) -> List[Tuple[str, float]]:
        if not self.initialized:
            self._llm_initialize()

        task = (
            'Given a web search query, retrieve relevant '
            'passages that answer the query'
        )

        pairs = [
            qwen_rerank_format_instruction(task, query, doc) 
            for doc in documents
        ]

        # Tokenize the input texts
        inputs = self._rerank_process_inputs(pairs)
        scores = self._rerank_compute_logits(inputs)

        return scores

    def vision(self, image_path: str, prompt: str, system_prompt: str = SYSTEM_PROMPT):
        raise NotImplementedError("Vision model not implemented for QwenLLM")

class OllamaLLM:
    def __init__(self, model_name: str = ''):
        self.model_name = model_name

    def embed_text(self, text: str):
        return ollama.embed(model=self.model_name, text=text)

    def chat(self, prompts: str | List[str], stream: bool = True, system_prompt: str = SYSTEM_PROMPT):
        if isinstance(prompts, str):
            prompts = [prompts]
        if stream:
            assert len(prompts) == 1, "Streaming mode only supports one prompt"
        for prompt in prompts:
            response = ollama.chat(model=self.model_name, messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ], stream=stream)

            if stream:
                for chunk in response:
                    yield OutputContent(content=chunk.message.content)
            else:
                yield OutputContent(content=response.message.content)
    
    def vision(self, image_path: str, prompt: str, system_prompt: str = SYSTEM_PROMPT):
        raise NotImplementedError("Vision model not implemented for Ollama")

class OpenAILLM:
    def __init__(self, model_name: str = '', base_url: str = 'http://localhost:6379/v1', api_key: str = ''):
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key
        self.client = OpenAI(
            api_key=self.api_key, 
            base_url=self.base_url,
            timeout=30,
        )

    def embed_text(self, text: str):
        response = self.client.embeddings.create(model=self.model_name, input=text)
        embeddings = [
            d.embedding
            for d in response.data
        ]
        return embeddings

    def chat(self, prompts: str | List[str], stream: bool = True, system_prompt: str = SYSTEM_PROMPT):
        if isinstance(prompts, str):
            prompts = [prompts]
        if stream:
            assert len(prompts) == 1, "Streaming mode only supports one prompt"
        for prompt in prompts:
            response = self.client.chat.completions.create(model=self.model_name, messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ], stream=stream)

            if stream:
                for chunk in response:
                    yield OutputContent(content=chunk.message.content)
            else:
                yield OutputContent(content=response.choices[0].message.content)

    def rerank(self, query: str, documents: List[str]) -> List[Tuple[str, float]]:
        return self.client.rerank.create(model=self.model_name, inputs=documents, query=query)

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