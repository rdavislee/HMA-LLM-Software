#!/usr/bin/env python3
"""
Development startup script for HMA-LLM Software Construction.
Starts the backend WebSocket server and provides frontend instructions.
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from server import HMAServer

async def start_backend():
    """Start the backend WebSocket server."""
    print("🚀 Starting HMA-LLM Backend Server...")
    print("📍 WebSocket server will be available at: ws://localhost:8080/ws")
    print("📁 Generated projects will be saved to: generated_projects/")
    print()
    
    server = HMAServer(host="localhost", port=8080)
    await server.start()

def start_frontend():
    """Provide instructions for starting the frontend."""
    frontend_dir = Path(__file__).parent.parent / "new_frontend"
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        print("Please ensure the 'new_frontend' directory exists.")
        return
    
    print("🌐 Frontend Setup Instructions:")
    print("1. Open a new terminal window")
    print(f"2. Navigate to: {frontend_dir}")
    print("3. Install dependencies: npm install")
    print("4. Start the development server: npm run dev")
    print("5. Open your browser to the URL shown by Vite")
    print()
    print("📝 The frontend will automatically connect to the backend WebSocket server.")
    print()

def main():
    """Main entry point."""
    print("=" * 60)
    print("🎯 HMA-LLM Software Construction - Development Mode")
    print("=" * 60)
    print()
    
    # Check if required dependencies are installed
    try:
        import websockets
        print("✅ WebSocket dependencies found")
    except ImportError:
        print("❌ Missing WebSocket dependencies!")
        print("Please install required packages:")
        print("pip install -r requirements.txt")
        return
    
    # Start frontend instructions
    start_frontend()
    
    # Start backend server
    try:
        asyncio.run(start_backend())
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main() 