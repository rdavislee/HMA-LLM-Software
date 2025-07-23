#!/usr/bin/env python3
"""
Quick non-interactive test for LLM interface.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from llm.providers import get_llm_client, ConsoleLLMClient
from llm.base import BaseLLMClient


def test_imports():
    """Test that LLM modules can be imported."""
    print("Testing imports...")
    print("[OK] Successfully imported LLM modules")
    return True


def test_factory():
    """Test the get_llm_client factory function."""
    print("\nTesting factory function...")
    
    # Test console client
    client = get_llm_client("console")
    assert isinstance(client, ConsoleLLMClient)
    assert isinstance(client, BaseLLMClient)
    print("[OK] Console client created")
    
    # Test invalid model
    try:
        get_llm_client("invalid-model")
        print("[FAIL] Should have raised ValueError")
        return False
    except ValueError as e:
        print(f"[OK] Correctly raised error: {str(e)[:50]}...")
    
    return True


def test_model_list():
    """Test available models."""
    print("\nTesting model list...")
    
    from llm.providers import MODEL_CLIENTS
    
    print(f"Total models available: {len(MODEL_CLIENTS)}")
    print("\nModels by provider:")
    
    providers = {
        "OpenAI": ["gpt-4o", "gpt-4.1", "o3", "o3-pro"],
        "Anthropic": ["claude-sonnet-4", "claude-opus-4", "claude-3.7-sonnet", "claude-3.5-sonnet"],
        "Google": ["gemini-2.5-flash", "gemini-2.5-pro"],
        "DeepSeek": ["deepseek-v3", "deepseek-r1"],
        "xAI": ["grok-3", "grok-3-mini"],
        "Testing": ["console"]
    }
    
    for provider, models in providers.items():
        available = [m for m in models if m in MODEL_CLIENTS]
        print(f"  {provider}: {len(available)}/{len(models)} models")
    
    return True


def test_api_keys():
    """Check which API keys are configured."""
    print("\nChecking API keys...")
    
    keys = {
        "OpenAI": "OPENAI_API_KEY",
        "Anthropic": "ANTHROPIC_API_KEY",
        "Google": "GOOGLE_GEMINI_API_KEY",
        "DeepSeek": "DEEPSEEK_API_KEY",
        "xAI": "XAI_API_KEY"
    }
    
    configured = 0
    for provider, env_var in keys.items():
        if os.getenv(env_var):
            print(f"  [OK] {provider} key configured")
            configured += 1
        else:
            print(f"  [--] {provider} key not set")
    
    print(f"\nTotal configured: {configured}/{len(keys)}")
    return True


async def test_console_mock():
    """Test console client with mocked input."""
    print("\nTesting console client structure...")
    
    client = get_llm_client("console")
    
    # Test properties
    print(f"  Supports system role: {client.supports_system_role}")
    print(f"  Client type: {type(client).__name__}")
    
    # Test that methods exist
    assert hasattr(client, 'generate_response')
    assert hasattr(client, 'generate_structured_response')
    print("  [OK] All required methods present")
    
    return True


def main():
    """Run all tests."""
    print("LLM Interface Quick Test")
    print("=" * 40)
    
    results = []
    
    # Synchronous tests
    results.append(("Imports", test_imports()))
    results.append(("Factory", test_factory()))
    results.append(("Model List", test_model_list()))
    results.append(("API Keys", test_api_keys()))
    
    # Async tests
    results.append(("Console Mock", asyncio.run(test_console_mock())))
    
    print("\n" + "=" * 40)
    print("Test Results:")
    passed = sum(1 for _, result in results if result)
    print(f"  Passed: {passed}/{len(results)}")
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")
    
    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)