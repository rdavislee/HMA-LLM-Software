"""
Full integration test for the HMA-LLM system.
Tests the complete flow from frontend prompt to code generation.
"""

import asyncio
import json
import pytest
import websockets
from pathlib import Path
import sys
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from server import HMAServer
from llm.providers import ConsoleLLMClient

@pytest.mark.asyncio
async def test_full_integration():
    """Test the complete integration from prompt to code generation."""
    # Start server
    server = HMAServer(host="localhost", port=8083)
    server_task = asyncio.create_task(server.start())
    
    # Wait for server to start
    await asyncio.sleep(0.5)
    
    try:
        # Connect as a client
        async with websockets.connect("ws://localhost:8083/ws") as websocket:
            # Wait for welcome message
            message = await websocket.recv()
            data = json.loads(message)
            
            assert data["type"] == "message"
            assert "Welcome to HMA-LLM" in data["payload"]["content"]
            print(f"✅ Received welcome: {data['payload']['content']}")
            
            # Send a prompt
            prompt = "Create a simple Python hello world script"
            await websocket.send(json.dumps({
                "type": "prompt",
                "payload": {
                    "agentId": "root",
                    "prompt": prompt
                }
            }))
            print(f"📤 Sent prompt: {prompt}")
            
            # Collect responses
            messages_received = []
            agent_updates = []
            code_streams = []
            file_updates = []
            
            # Wait for responses (with timeout)
            start_time = time.time()
            timeout = 30  # 30 seconds timeout
            
            while time.time() - start_time < timeout:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    
                    if data["type"] == "message":
                        messages_received.append(data["payload"])
                        print(f"💬 Message: {data['payload']['content'][:100]}...")
                        
                    elif data["type"] == "agent_update":
                        agent_updates.append(data["payload"])
                        print(f"🤖 Agent Update: {data['payload']['agentId']} - {data['payload']['status']}")
                        
                    elif data["type"] == "code_stream":
                        code_streams.append(data["payload"])
                        if data["payload"]["isComplete"]:
                            print(f"📝 Code Complete: {data['payload']['filePath']}")
                            
                    elif data["type"] == "file_tree_update":
                        file_updates.append(data["payload"])
                        print(f"📁 File Update: {data['payload']['action']} {data['payload']['filePath']}")
                        
                    elif data["type"] == "project_status":
                        print(f"🚀 Project Status: {data['payload']['status']}")
                        if data["payload"]["status"] == "completed":
                            break
                            
                except asyncio.TimeoutError:
                    # Check if we're done
                    if any(update.get("status") == "completed" for update in agent_updates):
                        break
                    continue
            
            # Verify we received expected responses
            assert len(messages_received) > 0, "Should receive at least one message"
            assert len(agent_updates) > 0, "Should receive agent updates"
            
            # Check that agents were activated
            active_agents = [u for u in agent_updates if u["status"] == "active"]
            assert len(active_agents) > 0, "At least one agent should be activated"
            
            print("\n📊 Summary:")
            print(f"  Messages: {len(messages_received)}")
            print(f"  Agent Updates: {len(agent_updates)}")
            print(f"  Code Streams: {len(code_streams)}")
            print(f"  File Updates: {len(file_updates)}")
            
    finally:
        # Clean up
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in the integration."""
    server = HMAServer(host="localhost", port=8084)
    server_task = asyncio.create_task(server.start())
    
    await asyncio.sleep(0.5)
    
    try:
        async with websockets.connect("ws://localhost:8084/ws") as websocket:
            # Skip welcome message
            await websocket.recv()
            
            # Send invalid message
            await websocket.send("invalid json")
            
            # Should still be connected
            assert websocket.open
            
            # Send message with invalid type
            await websocket.send(json.dumps({
                "type": "invalid_type",
                "payload": {}
            }))
            
            # Should still be connected
            assert websocket.open
            
            print("✅ Error handling tests passed")
            
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    print("🧪 Running Full Integration Tests...")
    
    # Run tests
    asyncio.run(test_full_integration())
    asyncio.run(test_error_handling())
    
    print("\n✅ All integration tests passed!") 