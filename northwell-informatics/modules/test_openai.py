#!/usr/bin/env python3
"""
Test script for OpenAILLM class
This script tests basic functionality of the OpenAI LLM wrapper.
"""

import sys
import os
import time
from typing import List

# Add the current directory to Python path to import openai module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openai import OpenAILLM


def test_basic_initialization():
    """Test basic LLM initialization with default parameters."""
    print("🔧 Testing basic initialization...")
    
    try:
        llm = OpenAILLM()
        print(f"✅ Successfully initialized OpenAILLM with model: {llm.model}")
        print(f"   - Temperature: {llm.temp}")
        print(f"   - Max tokens: {llm.max_tokens}")
        print(f"   - Top-p: {llm.top_p}")
        return llm
    except Exception as e:
        print(f"❌ Failed to initialize OpenAILLM: {e}")
        return None


def test_custom_initialization():
    """Test LLM initialization with custom parameters."""
    print("\n🔧 Testing custom initialization...")
    
    try:
        llm = OpenAILLM(
            model="gpt-4o-mini",
            temp=0.7,
            max_tokens=150,
            top_p=0.9
        )
        print(f"✅ Successfully initialized custom OpenAILLM")
        print(f"   - Model: {llm.model}")
        print(f"   - Temperature: {llm.temp}")
        print(f"   - Max tokens: {llm.max_tokens}")
        print(f"   - Top-p: {llm.top_p}")
        return llm
    except Exception as e:
        print(f"❌ Failed to initialize custom OpenAILLM: {e}")
        return None


def test_simple_prompt(llm: OpenAILLM):
    """Test a simple prompt."""
    print("\n💬 Testing simple prompt...")
    
    try:
        prompt = "What is 2+2? Answer with just the number."
        print(f"   Prompt: '{prompt}'")
        
        start_time = time.time()
        response = llm(prompt)
        end_time = time.time()
        
        print(f"✅ Response received in {end_time - start_time:.2f} seconds")
        print(f"   Response: '{response}'")
        return True
    except Exception as e:
        print(f"❌ Failed to get response: {e}")
        return False


def test_complex_prompt(llm: OpenAILLM):
    """Test a more complex prompt."""
    print("\n🧠 Testing complex prompt...")
    
    try:
        prompt = """Explain the concept of machine learning in exactly 2 sentences. 
        Make it simple enough for a beginner to understand."""
        print(f"   Prompt: '{prompt}'")
        
        start_time = time.time()
        response = llm(prompt)
        end_time = time.time()
        
        print(f"✅ Response received in {end_time - start_time:.2f} seconds")
        print(f"   Response: '{response}'")
        return True
    except Exception as e:
        print(f"❌ Failed to get response: {e}")
        return False


def test_stop_sequences(llm: OpenAILLM):
    """Test stop sequences functionality."""
    print("\n⏹️  Testing stop sequences...")
    
    try:
        prompt = "Count from 1 to 10: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10. Now count again:"
        stop_sequences = [", 5"]
        
        print(f"   Prompt: '{prompt}'")
        print(f"   Stop sequences: {stop_sequences}")
        
        start_time = time.time()
        response = llm._call(prompt, stop=stop_sequences)
        end_time = time.time()
        
        print(f"✅ Response received in {end_time - start_time:.2f} seconds")
        print(f"   Response: '{response}'")
        print(f"   Expected to stop at ', 5'")
        return True
    except Exception as e:
        print(f"❌ Failed to test stop sequences: {e}")
        return False


def test_different_models():
    """Test different OpenAI models."""
    print("\n🔄 Testing different models...")
    
    models_to_test = ["gpt-4o-mini", "gpt-3.5-turbo"]
    prompt = "Say 'Hello from {model}' where {model} is your model name."
    
    for model in models_to_test:
        try:
            print(f"   Testing model: {model}")
            llm = OpenAILLM(model=model, max_tokens=50)
            
            start_time = time.time()
            response = llm(prompt.replace("{model}", model))
            end_time = time.time()
            
            print(f"   ✅ {model} responded in {end_time - start_time:.2f}s: '{response}'")
        except Exception as e:
            print(f"   ❌ {model} failed: {e}")


def test_error_handling():
    """Test error handling with invalid API key."""
    print("\n⚠️  Testing error handling...")
    
    try:
        # Test with invalid API key
        llm = OpenAILLM(api_key="invalid_key")
        response = llm("Hello")
        print(f"❌ Expected error but got response: {response}")
    except Exception as e:
        print(f"✅ Correctly handled invalid API key: {type(e).__name__}")
    
    try:
        # Test with empty API key
        llm = OpenAILLM(api_key="")
        response = llm("Hello")
        print(f"❌ Expected error but got response: {response}")
    except ValueError as e:
        print(f"✅ Correctly handled empty API key: {e}")
    except Exception as e:
        print(f"⚠️  Unexpected error type: {type(e).__name__}: {e}")


def run_all_tests():
    """Run all tests."""
    print("🚀 Starting OpenAI LLM Tests")
    print("=" * 50)
    
    # Test initialization
    llm = test_basic_initialization()
    if not llm:
        print("❌ Cannot proceed with tests - initialization failed")
        return
    
    # Test custom initialization
    custom_llm = test_custom_initialization()
    
    # Test API calls
    test_simple_prompt(llm)
    test_complex_prompt(llm)
    test_stop_sequences(llm)
    
    # Test different models
    test_different_models()
    
    # Test error handling
    test_error_handling()
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed!")


def interactive_test():
    """Interactive test mode where user can input custom prompts."""
    print("\n🎮 Interactive Test Mode")
    print("Enter prompts to test the LLM. Type 'quit' to exit.")
    print("-" * 40)
    
    try:
        llm = OpenAILLM(temp=0.7, max_tokens=200)
        print(f"Using model: {llm.model}")
        
        while True:
            user_prompt = input("\nPrompt: ").strip()
            
            if user_prompt.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_prompt:
                continue
            
            try:
                print("Thinking...")
                start_time = time.time()
                response = llm(user_prompt)
                end_time = time.time()
                
                print(f"Response ({end_time - start_time:.2f}s): {response}")
            except Exception as e:
                print(f"Error: {e}")
    
    except Exception as e:
        print(f"Failed to initialize interactive mode: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        run_all_tests()
        
        # Ask if user wants to try interactive mode
        try:
            choice = input("\nWould you like to try interactive mode? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                interactive_test()
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
