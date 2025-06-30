#!/usr/bin/env python3
"""
Development server startup script for HMA-LLM.
Starts the WebSocket backend server.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if environment is properly configured."""
    env_file = project_root / '.env'
    if not env_file.exists():
        logger.warning("⚠️  No .env file found. Creating from template...")
        
        # Create .env from example
        env_example = project_root / 'config' / 'env_example'
        if env_example.exists():
            env_content = env_example.read_text()
            env_file.write_text(env_content)
            logger.info("✅ Created .env file. Please add your API keys.")
        else:
            # Create minimal .env
            env_content = """# HMA-LLM Environment Configuration
# Add at least one API key to use the system

# OpenAI
OPENAI_API_KEY=

# Anthropic
ANTHROPIC_API_KEY=

# Google AI (Gemini)
GOOGLE_GEMINI_API_KEY=

# Server Configuration
HOST=localhost
PORT=8080
"""
            env_file.write_text(env_content)
            logger.info("✅ Created minimal .env file. Please add your API keys.")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check if at least one API key is configured
    api_keys = {
        'OpenAI': os.getenv('OPENAI_API_KEY'),
        'Anthropic': os.getenv('ANTHROPIC_API_KEY'),
        'Google': os.getenv('GOOGLE_GEMINI_API_KEY'),
        'DeepSeek': os.getenv('DEEPSEEK_API_KEY')
    }
    
    configured_keys = [name for name, key in api_keys.items() if key and key.strip()]
    
    if not configured_keys:
        logger.warning("⚠️  No API keys configured. The system will use mock responses.")
        logger.warning("   To use real LLMs, add API keys to the .env file.")
    else:
        logger.info(f"✅ Configured LLM providers: {', '.join(configured_keys)}")

async def main():
    """Main entry point."""
    logger.info("🚀 Starting HMA-LLM Development Server...")
    
    # Check environment
    check_environment()
    
    # Create required directories
    generated_dir = project_root / 'generated_projects'
    generated_dir.mkdir(exist_ok=True)
    
    try:
        # Import and start server
        from src.server import HMAServer
        
        host = os.getenv('HOST', 'localhost')
        port = int(os.getenv('PORT', '8080'))
        
        server = HMAServer(host=host, port=port)
        
        logger.info(f"✅ Server starting on ws://{host}:{port}/ws")
        logger.info("📝 To start the frontend, run: cd frontend && npm run dev")
        logger.info("🛑 Press Ctrl+C to stop the server")
        
        await server.start()
        
    except ImportError as e:
        logger.error(f"❌ Failed to import server: {e}")
        logger.error("   Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down server...")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!") 