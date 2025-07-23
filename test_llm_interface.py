#!/usr/bin/env python3
"""
Simple test script to verify LLM interface functionality.
Tests basic operations without requiring actual API calls.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from llm.providers import get_llm_client, ConsoleLLMClient
from llm.base import BaseLLMClient


async def test_console_client():
    """Test the console LLM client for manual testing."""
    print("\nTesting Console LLM Client...")
    print("-" * 50)
    
    client = get_llm_client("console")
    assert isinstance(client, ConsoleLLMClient)
    assert isinstance(client, BaseLLMClient)
    print("[OK] Console client created successfully")
    
    # Test properties
    print(f"[OK] Supports system role: {client.supports_system_role}")
    
    # Test basic response generation
    print("\nTesting generate_response...")
    print("When prompted, type a test response and press Enter twice:")
    
    messages = [{"role": "user", "content": "Hello, this is a test"}]
    response = await client.generate_response(messages, temperature=0.5)
    print(f"[OK] Received response: {response[:50]}...")
    
    return True


async def test_factory_function():
    """Test the LLM client factory function."""
    print("\nTesting LLM Factory Function...")
    print("-" * 50)
    
    # Test valid models
    test_models = ["console", "gpt-4o", "claude-opus-4", "gemini-2.5-flash"]
    
    for model in test_models:
        try:
            client = get_llm_client(model)
            print(f"[OK] Created client for model: {model}")
            print(f"   - Type: {type(client).__name__}")
            print(f"   - Supports system role: {client.supports_system_role}")
        except Exception as e:
            print(f"[FAIL] Failed to create client for {model}: {e}")
    
    # Test invalid model
    try:
        get_llm_client("invalid-model-xyz")
        print("[FAIL] Should have raised error for invalid model")
    except ValueError as e:
        print(f"[OK] Correctly raised error for invalid model: {e}")
    
    return True


async def test_available_providers():
    """Check which LLM providers have API keys configured."""
    print("\nChecking Available LLM Providers...")
    print("-" * 50)
    
    providers = {
        "OpenAI": "OPENAI_API_KEY",
        "Anthropic": "ANTHROPIC_API_KEY", 
        "Google": "GOOGLE_GEMINI_API_KEY",
        "DeepSeek": "DEEPSEEK_API_KEY",
        "xAI": "XAI_API_KEY"
    }
    
    available = []
    for provider, env_var in providers.items():
        if os.getenv(env_var):
            print(f"[OK] {provider}: API key found")
            available.append(provider)
        else:
            print(f"[MISSING] {provider}: No API key set ({env_var})")
    
    print(f"\nTotal available providers: {len(available)}/{len(providers)}")
    return available


async def test_api_call(model_name: str):
    """Test an actual API call to a provider."""
    print(f"\nTesting API call to {model_name}...")
    print("-" * 50)
    
    try:
        client = get_llm_client(model_name)
        messages = [{"role": "user", "content": "Say 'Hello, LLM test successful!' and nothing else."}]
        
        response = await client.generate_response(
            messages=messages,
            temperature=0.1,
            max_tokens=50
        )
        
        print(f"[OK] API call successful!")
        print(f"Response: {response}")
        return True
    except Exception as e:
        print(f"[FAIL] API call failed: {e}")
        return False


async def main():
    """Run all LLM interface tests."""
    print("HMA-LLM Interface Test Suite")
    print("=" * 50)
    
    # Test 1: Factory function
    await test_factory_function()
    
    # Test 2: Check available providers
    available = await test_available_providers()
    
    # Test 3: Console client (manual test)
    print("\n" + "="*50)
    choice = input("Do you want to test the Console LLM Client? (y/n): ")
    if choice.lower() == 'y':
        await test_console_client()
    
    # Test 4: Real API call (optional)
    if available:
        print("\n" + "="*50)
        print("Available providers for API testing:")
        for i, provider in enumerate(available):
            print(f"{i+1}. {provider}")
        print("0. Skip API testing")
        
        choice = input("\nSelect a provider to test (0 to skip): ")
        if choice.isdigit() and 0 < int(choice) <= len(available):
            provider = available[int(choice) - 1]
            # Map provider to a model
            model_map = {
                "OpenAI": "gpt-4o",
                "Anthropic": "claude-3.5-sonnet",
                "Google": "gemini-2.5-flash",
                "DeepSeek": "deepseek-v3",
                "xAI": "grok-3-mini"
            }
            model = model_map.get(provider)
            if model:
                await test_api_call(model)
    
    print("\n" + "="*50)
    print("[DONE] LLM Interface test suite completed!")


if __name__ == "__main__":
    asyncio.run(main())