#!/usr/bin/env python3
"""
Test server using console mode for manual testing without API costs.
This allows you to test the integration by manually providing responses.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path("src")))

from server import HMAServer

async def main():
    """Run the server in console mode."""
    print("🚀 Starting HMA-LLM Server in Console Mode")
    print("📝 You will be prompted to provide responses manually")
    print("🌐 Frontend will be available at http://localhost:5173")
    print("=" * 50)
    
    # Create server instance
    server = HMAServer(host="localhost", port=8080)
    
    # Modify the server to use console mode
    # We need to patch the get_llm_client call
    import src.llm.providers as providers
    
    # Store original function
    original_get_llm_client = providers.get_llm_client
    
    # Create a patched version that always returns console client
    def patched_get_llm_client(model_name: str = "console"):
        print(f"🔧 Using console mode instead of {model_name}")
        return original_get_llm_client("console")
    
    # Replace the function
    providers.get_llm_client = patched_get_llm_client
    
    print("✅ Server configured for console mode")
    print("💡 When you send a prompt from the frontend, you'll be asked to provide the response manually")
    
    # Start the server
    await server.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}") 