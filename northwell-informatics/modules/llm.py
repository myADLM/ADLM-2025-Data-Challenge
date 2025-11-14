"""
Unified LLM module supporting both Northwell and OpenAI APIs.
This module provides a single interface to work with multiple LLM providers.
"""

import requests
import base64
from typing import Any, List, Mapping, Optional, Literal, Union

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM as BaseLLM
from pydantic import Field

from config import LLMConfig


class LLM(BaseLLM):
    """
    Unified LLM class that supports both Northwell and OpenAI APIs.
    
    Usage:
        # Use default provider (Northwell)
        llm = LLM()
        
        # Use specific provider
        llm = LLM(provider="openai")
        
        # Use with custom parameters
        llm = LLM(
            provider="openai",
            model="gpt-4o",
            temp=0.7,
            max_tokens=500
        )
    """
    
    # Define Pydantic fields
    provider: str = Field(default="northwell")
    model: str = Field(default="")
    temp: float = Field(default=0.0)
    max_tokens: int = Field(default=1000)
    top_p: float = Field(default=0.95)
    config: dict = Field(default_factory=dict, exclude=True)
    
    def __init__(
        self,
        *,
        provider: Optional[Literal["northwell", "openai"]] = None,
        model: Optional[str] = None,
        temp: float = None,
        max_tokens: int = None,
        top_p: float = None,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the LLM with configurable parameters.
        
        Args:
            provider: The LLM provider to use ('northwell' or 'openai')
            model: The model to use (must be available for the provider)
            temp: Temperature for randomness
            max_tokens: Maximum tokens to generate
            top_p: Top-p sampling parameter
            api_key: API key (overrides config file)
            **kwargs: Additional keyword arguments
        """
        # Set provider
        provider = provider or LLMConfig.DEFAULT_PROVIDER
        
        # Get provider configuration
        config = LLMConfig.get_config(provider)
        
        # Override API key if provided
        if api_key:
            config["api_key"] = api_key
        
        # Set model
        model = model or config["default_model"]
        if not LLMConfig.validate_model(provider, model):
            raise ValueError(f"Model '{model}' not available for provider '{provider}'")
        
        # Set parameters with defaults from config
        defaults = LLMConfig.DEFAULT_PARAMS
        temp = temp if temp is not None else defaults["temperature"]
        max_tokens = max_tokens if max_tokens is not None else defaults["max_tokens"]
        top_p = top_p if top_p is not None else defaults["top_p"]
        
        # Validate API key
        if not config["api_key"]:
            raise ValueError(f"API key required for provider '{provider}'. "
                           f"Set it in config.py or pass as parameter.")
        
        # Initialize with Pydantic
        super().__init__(
            provider=provider,
            model=model,
            temp=temp,
            max_tokens=max_tokens,
            top_p=top_p,
            config=config,
            **kwargs
        )

    @property
    def _llm_type(self) -> str:
        return f"{self.provider}_{self.model}"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the appropriate provider API based on configuration."""
        
        if self.provider == "northwell":
            return self._call_northwell(prompt, stop, **kwargs)
        elif self.provider == "openai":
            return self._call_openai(prompt, stop, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _call_northwell(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any
    ) -> str:
        """Call Northwell API."""
        
        headers = {
            'X-API-Key': self.config["api_key"],
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        data = {
            "ad_object_id": self.config["ad_object_id"],
            "advanced": {
                "max_tokens": self.max_tokens,
                "temperature": self.temp,
                "top_p": self.top_p
            },
            "context": "",
            "debug": False,
            "models": [self.model],
            "prompt": base64.b64encode(prompt.encode("utf-8")).decode("utf-8")
        }

        r = requests.post(self.config["base_url"], headers=headers, json=data)
        r.raise_for_status()

        response = r.json()['data']['generative_responses'][0]['response']
        
        # Implement stop functionality by truncating the response
        if stop is not None and len(stop) > 0:
            earliest_stop_pos = len(response)
            for stop_seq in stop:
                if stop_seq in response:
                    stop_pos = response.find(stop_seq)
                    if stop_pos < earliest_stop_pos:
                        earliest_stop_pos = stop_pos
            
            if earliest_stop_pos < len(response):
                response = response[:earliest_stop_pos]
        
        return response

    def _call_openai(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any
    ) -> str:
        """Call OpenAI API."""
        
        headers = {
            'Authorization': f'Bearer {self.config["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        # Prepare messages for chat completion
        messages = [{"role": "user", "content": prompt}]
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temp,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p
        }
        
        # Add stop sequences if provided
        if stop is not None and len(stop) > 0:
            data["stop"] = stop

        r = requests.post(self.config["base_url"], headers=headers, json=data)
        r.raise_for_status()

        response = r.json()['choices'][0]['message']['content']
        return response

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            "provider": self.provider,
            "model": self.model,
            "base_url": self.config["base_url"],
            "temperature": self.temp,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p
        }

    def get_available_models(self) -> List[str]:
        """Get list of available models for current provider."""
        return self.config["available_models"]

    def switch_provider(
        self,
        provider: Literal["northwell", "openai"],
        model: Optional[str] = None
    ) -> None:
        """
        Switch to a different provider and optionally change model.
        
        Args:
            provider: New provider to use
            model: Optional model to switch to (uses default if not specified)
        """
        self.provider = provider
        self.config = LLMConfig.get_config(provider)
        
        if model:
            if not LLMConfig.validate_model(provider, model):
                raise ValueError(f"Model '{model}' not available for provider '{provider}'")
            self.model = model
        else:
            self.model = self.config["default_model"]
        
        if not self.config["api_key"]:
            raise ValueError(f"API key required for provider '{provider}'. "
                           f"Set it in config.py")

    def __repr__(self) -> str:
        return (f"LLM(provider='{self.provider}', model='{self.model}', "
                f"temp={self.temp}, max_tokens={self.max_tokens})")


# Convenience functions for quick access
def create_northwell_llm(**kwargs) -> LLM:
    """Create a LLM instance configured for Northwell."""
    return LLM(provider="northwell", **kwargs)


def create_openai_llm(**kwargs) -> LLM:
    """Create a LLM instance configured for OpenAI."""
    return LLM(provider="openai", **kwargs)


def create_llm(provider: str = None, **kwargs) -> LLM:
    """Create a LLM instance with the specified or default provider."""
    return LLM(provider=provider, **kwargs)


# Legacy compatibility - create instances that match the old classes
class NorthwellLLM(LLM):
    """Legacy compatibility class for NorthwellLLM."""
    def __init__(self, **kwargs):
        super().__init__(provider="northwell", **kwargs)


class OpenAILLM(LLM):
    """Legacy compatibility class for OpenAILLM."""
    def __init__(self, **kwargs):
        super().__init__(provider="openai", **kwargs)


if __name__ == "__main__":
    # Example usage
    print("LLM Examples")
    print("=" * 50)
    
    try:
        # Create Northwell LLM
        print("Creating Northwell LLM...")
        nw_llm = create_northwell_llm()
        print(f"✅ {nw_llm}")
        
        # Create OpenAI LLM (will fail if no API key)
        print("\nCreating OpenAI LLM...")
        try:
            ai_llm = create_openai_llm()
            print(f"✅ {ai_llm}")
        except ValueError as e:
            print(f"❌ {e}")
            print("   Set your OpenAI API key in config.py")
        
        # Show available models
        print(f"\nNorthwell models: {len(nw_llm.get_available_models())}")
        print(f"First few: {nw_llm.get_available_models()[:3]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
