import requests
import base64
from typing import Any, List, Mapping, Optional, Literal

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM


class NorthwellLLM(LLM):
    model: Literal[
        "o3",
        "o4-mini",
        "gpt-4.1",
        "gpt-4.1-nano",
        "gpt-4.1-mini",
        "claude-sonnet-4",
        "claude-opus-4",
        "claude-3.5-haiku",
        "gemini-2.0-flash",
        "gemini-1.5-pro",
        "o1-mini",
        "gpt-4o-mini",
        "gpt-4o",
        "claude-3.5-sonnet",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "o3-mini",
        "o1",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "claude-3.7-sonnet"
    ] = "claude-3.7-sonnet"
    temp: float = 0
    max_tokens: int = 10000 ## SC increasing from 1000 to allow use of each model's default max tokens
    top_p: float = 0.95
    
    llm_url: str = 'https://api.ai.northwell.edu/generative'
    X_API_Key: str = ''
    ad_object_id: str = ""

    def __init__(self, *, model: str = "claude-3.7-sonnet", temp: float = 0, max_tokens: int = 10000, top_p: float = 0.95, **kwargs):
        """
        Initialize the NorthwellLLM with configurable parameters.
        
        Args:
            model: The model to use (keyword-only)
            temp: Temperature for randomness (keyword-only)
            max_tokens: Maximum tokens to generate (keyword-only)
            top_p: Top-p sampling parameter (keyword-only)
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)
        self.model = model
        self.temp = temp
        self.max_tokens = max_tokens
        self.top_p = top_p
        print(f"NorthwellLLM initialized with max_tokens: {self.max_tokens}")  # Add this line

    @property
    def _llm_type(self) -> str:
        return self.model

    def _call(
                    self,
                    prompt: str,
                    stop: Optional[List[str]] = None,
                    run_manager: Optional[CallbackManagerForLLMRun] = None,
                    **kwargs: Any,
                ) -> str:
        
        headers = {
            'X-API-Key' : self.X_API_Key,
            'accept' : 'application/json',
            'Content-Type' : 'application/json'
        }
        
        data = {
          "ad_object_id": self.ad_object_id,
          "advanced": {
            "max_tokens": self.max_tokens,
            "temperature": self.temp,
            "top_p": self.top_p
          },
          "context": "",
          "debug": False,
          "models": [
            self.model
          ],
          "prompt": base64.b64encode(prompt.encode("utf-8")).decode("utf-8")
        }

        r = requests.post(self.llm_url, headers=headers, json=data)

        r.raise_for_status()

        response = r.json()['data']['generative_responses'][0]['response']
        
        # Implement stop functionality by truncating the response
        if stop is not None and len(stop) > 0:
            # Find the earliest occurrence of any stop sequence
            earliest_stop_pos = len(response)
            for stop_seq in stop:
                if stop_seq in response:
                    stop_pos = response.find(stop_seq)
                    if stop_pos < earliest_stop_pos:
                        earliest_stop_pos = stop_pos
            
            # Truncate the response at the stop sequence
            if earliest_stop_pos < len(response):
                response = response[:earliest_stop_pos]
        
        return response

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"llmUrl": self.llm_url}