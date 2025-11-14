"""
Configuration file for LLM APIs
This file contains API keys and configuration for different LLM providers.
"""

import os
from typing import Literal, Optional

class LLMConfig:
    """Configuration class for LLM providers"""
    
    # Default provider - can be 'northwell' or 'openai'
    DEFAULT_PROVIDER: Literal["northwell", "openai"] = "openai"
    
    # Northwell API Configuration
    NORTHWELL_CONFIG = {
        "api_key": "",
        "ad_object_id": "",
        "base_url": "https://api.ai.northwell.edu/generative",
        "default_model": "o3",
        "available_models": [
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
        ]
    }
    
    # OpenAI API Configuration
    OPENAI_CONFIG = {
        "api_key": "",  # Set your OpenAI API key here or use environment variable
        "base_url": "https://api.openai.com/v1/chat/completions",
        "default_model": "gpt-4o-mini",
        "available_models": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo", 
            "gpt-4",
            "gpt-3.5-turbo",
            "o1-preview",
            "o1-mini",
            "o3",
            "o4-mini"
        ]
    }
    
    # Default LLM Parameters
    DEFAULT_PARAMS = {
        "temperature": 0,
        "max_tokens": 10000,
        "top_p": 0.95
    }
    
    # Rate limiting and threading configuration
    MULTITHREADING_ENABLED = False  # Default to off for safety
    RATE_LIMIT_SLEEP = 15  # Default sleep time in seconds between API calls
    
    @classmethod
    def get_api_key(cls, provider: str) -> Optional[str]:
        """
        Get API key for the specified provider.
        Checks environment variables first, then falls back to config.
        """
        if provider == "northwell":
            return os.getenv("NORTHWELL_API_KEY", cls.NORTHWELL_CONFIG["api_key"])
        elif provider == "openai":
            return os.getenv("OPENAI_API_KEY", cls.OPENAI_CONFIG["api_key"])
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    @classmethod
    def get_config(cls, provider: str) -> dict:
        """Get full configuration for the specified provider."""
        if provider == "northwell":
            config = cls.NORTHWELL_CONFIG.copy()
            config["api_key"] = cls.get_api_key("northwell")
            return config
        elif provider == "openai":
            config = cls.OPENAI_CONFIG.copy()
            config["api_key"] = cls.get_api_key("openai")
            return config
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    @classmethod
    def validate_model(cls, provider: str, model: str) -> bool:
        """Validate if a model is available for the specified provider."""
        config = cls.get_config(provider)
        return model in config["available_models"]
    
    @classmethod
    def set_default_provider(cls, provider: Literal["northwell", "openai"]):
        """Set the default provider."""
        cls.DEFAULT_PROVIDER = provider
    
    @classmethod
    def is_multithreading_enabled(cls) -> bool:
        """Check if multithreading is enabled."""
        return cls.MULTITHREADING_ENABLED
    
    @classmethod
    def get_rate_limit_sleep(cls) -> int:
        """Get the rate limit sleep time in seconds."""
        return cls.RATE_LIMIT_SLEEP
    
    @classmethod
    def set_multithreading(cls, enabled: bool):
        """Enable or disable multithreading."""
        cls.MULTITHREADING_ENABLED = enabled
    
    @classmethod
    def set_rate_limit_sleep(cls, seconds: int):
        """Set the rate limit sleep time in seconds."""
        cls.RATE_LIMIT_SLEEP = seconds


# Example usage and setup instructions
if __name__ == "__main__":
    print("LLM Configuration Test")
    print("=" * 50)
    
    print(f"Default Provider: {LLMConfig.DEFAULT_PROVIDER}")
    
    northwell_key_status = 'Set' if LLMConfig.get_api_key('northwell') else 'Not Set'
    openai_key_status = 'Set' if LLMConfig.get_api_key('openai') else 'Not Set'
    
    print(f"\nNorthwell API Key: {northwell_key_status}")
    print(f"OpenAI API Key: {openai_key_status}")
    
    print(f"\nNorthwell Models: {len(LLMConfig.NORTHWELL_CONFIG['available_models'])}")
    print(f"OpenAI Models: {len(LLMConfig.OPENAI_CONFIG['available_models'])}")
    
    # Test API connection with hello world query
    print("\n" + "=" * 50)
    print("API Connection Test")
    print("=" * 50)
    
    def test_api(provider_name):
        """Test API connection with a simple query."""
        try:
            print(f"\n🧪 Testing {provider_name.title()} API...")
            
            # Get configuration
            config = LLMConfig.get_config(provider_name)
            print(f"   ✅ Configuration loaded: {config['default_model']}")
            
            # Test API call directly
            prompt = "Say 'Hello World' and nothing else."
            print(f"   📤 Sending: '{prompt}'")
            
            if provider_name == "northwell":
                response = test_northwell_api(config, prompt)
            elif provider_name == "openai":
                response = test_openai_api(config, prompt)
            else:
                raise ValueError(f"Unknown provider: {provider_name}")
            
            print(f"   📥 Response: '{response.strip()}'")
            return True
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_northwell_api(config, prompt):
        """Test Northwell API directly."""
        import requests
        import base64
        
        headers = {
            'X-API-Key': config["api_key"],
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        data = {
            "ad_object_id": config["ad_object_id"],
            "advanced": {
                "max_tokens": 50,
                "temperature": 0,
                "top_p": 0.95
            },
            "context": "",
            "debug": False,
            "models": [config["default_model"]],
            "prompt": base64.b64encode(prompt.encode("utf-8")).decode("utf-8")
        }

        r = requests.post(config["base_url"], headers=headers, json=data)
        r.raise_for_status()
        return r.json()['data']['generative_responses'][0]['response']
    
    def test_openai_api(config, prompt):
        """Test OpenAI API directly."""
        import requests
        
        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        messages = [{"role": "user", "content": prompt}]
        
        data = {
            "model": config["default_model"],
            "messages": messages,
            "temperature": 0,
            "max_tokens": 50,
            "top_p": 0.95
        }

        r = requests.post(config["base_url"], headers=headers, json=data)
        r.raise_for_status()
        return r.json()['choices'][0]['message']['content']
    
    # Test each provider that has an API key
    tested_any = False
    
    if LLMConfig.get_api_key('northwell'):
        tested_any = True
        test_api('northwell')
    else:
        print(f"\n⏭️  Skipping Northwell test - no API key")
    
    if LLMConfig.get_api_key('openai'):
        tested_any = True
        test_api('openai')
    else:
        print(f"\n⏭️  Skipping OpenAI test - no API key")
        print("\nTo set OpenAI API key:")
        print("1. Edit this file and set OPENAI_CONFIG['api_key']")
        print("2. Or set environment variable: export OPENAI_API_KEY='your-key-here'")
    
    if not tested_any:
        print("\n⚠️  No API keys found - cannot test connections")
        print("Set at least one API key to test functionality")
    
    print("\n" + "=" * 50)
    print("Configuration test complete!")