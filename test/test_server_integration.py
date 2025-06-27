"""
Integration test for the WebSocket server.
Tests basic connectivity and message handling.
"""

import asyncio
import json
import pytest
import websockets
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from server import HMAServer

@pytest.mark.asyncio
async def test_server_connection():
    """Test basic WebSocket server connection."""
    # Start server
    server = HMAServer(host="localhost", port=8081)  # Use different port for testing
    
    # Start server in background
    server_task = asyncio.create_task(server.start())
    
    # Wait a bit for server to start
    await asyncio.sleep(0.1)
    
    try:
        # Connect to server
        async with websockets.connect("ws://localhost:8081/ws") as websocket:
            # Wait for welcome message
            message = await websocket.recv()
            data = json.loads(message)
            
            assert data["type"] == "message"
            assert "Welcome to HMA-LLM" in data["payload"]["content"]
            
            # Send a test prompt
            await websocket.send(json.dumps({
                "type": "prompt",
                "payload": {
                    "agentId": "root",
                    "prompt": "Create a simple hello world program"
                }
            }))
            
            # Should receive an agent update
            message = await websocket.recv()
            data = json.loads(message)
            
            assert data["type"] == "agent_update"
            assert data["payload"]["status"] == "active"
            
    finally:
        # Clean up
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass

@pytest.mark.asyncio
async def test_server_message_handling():
    """Test server message handling."""
    server = HMAServer(host="localhost", port=8082)
    server_task = asyncio.create_task(server.start())
    
    await asyncio.sleep(0.1)
    
    try:
        async with websockets.connect("ws://localhost:8082/ws") as websocket:
            # Test invalid message
            await websocket.send(json.dumps({
                "type": "invalid_type",
                "payload": {}
            }))
            
            # Should not crash and should still be connected
            assert websocket.open
            
            # Test malformed JSON
            await websocket.send("invalid json")
            
            # Should still be connected
            assert websocket.open
            
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    # Run tests manually
    asyncio.run(test_server_connection())
    asyncio.run(test_server_message_handling())
    print("✅ All tests passed!") 