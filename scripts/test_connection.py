#!/usr/bin/env python3
"""
Test script to verify environment configuration and connection setup.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_environment():
    """Test environment configuration."""
    print("🧪 Testing Environment Configuration")
    print("=" * 40)
    
    # Load .env if it exists
    env_file = project_root / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print("✅ Loaded .env file")
        except ImportError:
            print("⚠️  python-dotenv not installed")
        except Exception as e:
            print(f"❌ Error loading .env: {e}")
    else:
        print("ℹ️  No .env file found, using system environment")
    
    # Test server configuration
    host = os.getenv("HMA_HOST", "localhost")
    port = int(os.getenv("HMA_PORT", "8080"))
    print(f"🌐 Server config: {host}:{port}")
    
    # Test API keys
    api_keys = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "Google Gemini": os.getenv("GOOGLE_GEMINI_API_KEY"),
        "DeepSeek": os.getenv("DEEPSEEK_API_KEY")
    }
    
    configured_providers = []
    for name, key in api_keys.items():
        if key and key.strip():
            configured_providers.append(name)
            # Show first 8 chars and last 4 chars for security
            masked_key = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "***"
            print(f"✅ {name}: {masked_key}")
    
    if not configured_providers:
        print("❌ No API keys configured!")
        return False
    
    print(f"✅ {len(configured_providers)} provider(s) configured")
    return True

def test_imports():
    """Test critical imports."""
    print("\n🔧 Testing Imports")
    print("=" * 40)
    
    try:
        import socketio
        print("✅ socketio")
    except ImportError as e:
        print(f"❌ socketio: {e}")
        return False
    
    try:
        from aiohttp import web
        print("✅ aiohttp")
    except ImportError as e:
        print(f"❌ aiohttp: {e}")
        return False
    
    try:
        from src.agents.base_agent import BaseAgent
        print("✅ src.agents")
    except ImportError as e:
        print(f"❌ src.agents: {e}")
        return False
    
    try:
        from src.llm.providers import get_llm_client
        print("✅ src.llm")
    except ImportError as e:
        print(f"❌ src.llm: {e}")
        return False
    
    return True

def main():
    """Main test function."""
    print("🚀 HMA-LLM Environment Test")
    print("=" * 50)
    
    # Test environment
    env_ok = test_environment()
    
    # Test imports
    imports_ok = test_imports()
    
    print("\n📋 Test Summary")
    print("=" * 40)
    
    if env_ok and imports_ok:
        print("✅ All tests passed! Ready to start the server.")
        print("\n💡 Next steps:")
        print("   python scripts/start_dev.py  # Start backend")
        print("   cd frontend && npm run dev   # Start frontend")
    else:
        print("❌ Some tests failed. Please check your configuration.")
        if not env_ok:
            print("   - Configure your .env file with API keys")
        if not imports_ok:
            print("   - Install dependencies: pip install -r requirements.txt")

if __name__ == "__main__":
    main() 