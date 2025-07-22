#!/usr/bin/env python3
"""
Development server startup script for HMA-LLM.
Starts the backend Socket.IO server with proper environment configuration.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_environment():
    """Check for required environment configuration."""
    env_file = project_root / ".env"
    env_example = project_root / "config" / "env.example"
    
    if not env_file.exists():
        print("⚠️  No .env file found!")
        print(f"📝 Please copy {env_example} to {env_file}")
        print("   and configure your API keys.")
        print()
        
        # Check if we have at least one API key set
        api_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_GEMINI_API_KEY", "DEEPSEEK_API_KEY"]
        has_api_key = any(os.getenv(key) for key in api_keys)
        
        if not has_api_key:
            print("❌ No LLM API keys found in environment!")
            print("   Please set at least one of:")
            for key in api_keys:
                print(f"   - {key}")
            print()
            return False
    
    # Load .env if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print(f"✅ Loaded environment from {env_file}")
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment")
    except Exception as e:
        print(f"⚠️  Could not load .env file: {e}")
    
    return True

def check_frontend_env():
    """Check frontend environment configuration."""
    frontend_dir = project_root / "frontend"
    frontend_env_dev = frontend_dir / ".env.development"
    frontend_env_example = frontend_dir / "config" / "env.example"
    
    if not frontend_env_dev.exists():
        print("ℹ️  Frontend environment not configured")
        print(f"📝 Optionally copy {frontend_env_example} to {frontend_env_dev}")
        print("   to customize frontend connection settings")
        print()

async def main():
    """Main entry point."""
    print("🚀 Starting HMA-LLM Development Server")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed. Please configure your environment and try again.")
        sys.exit(1)
    
    check_frontend_env()
    
    # Import and start server
    try:
        from src.server import main as server_main
        
        # Get configuration
        host = os.getenv("HMA_HOST", "localhost")
        port = int(os.getenv("HMA_PORT", "8080"))
        
        print(f"🌐 Backend server will start on http://{host}:{port}")
        print(f"🔌 WebSocket endpoint: ws://{host}:{port}/ws")
        print()
        print("💡 To start the frontend:")
        print("   cd frontend && npm run dev")
        print()
        print("📱 Frontend will be available at http://localhost:5173")
        print("=" * 50)
        
        # Start the server
        await server_main()
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        logging.exception("Server startup failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 