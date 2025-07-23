#!/usr/bin/env python3
"""Test script to verify LLM configuration integration between frontend and backend."""

import asyncio
import json
import socketio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_llm_integration():
    """Test the LLM configuration flow."""
    sio = socketio.AsyncClient()
    
    connected = False
    client_id = None
    
    @sio.event
    async def connect():
        nonlocal connected
        connected = True
        logger.info("Connected to server")
    
    @sio.event
    async def disconnect():
        logger.info("Disconnected from server")
    
    @sio.event
    async def message(data):
        """Handle messages from server."""
        nonlocal client_id
        
        if isinstance(data, str):
            data = json.loads(data)
        
        msg_type = data.get("type")
        payload = data.get("payload", {})
        
        logger.info(f"Received message type: {msg_type}")
        logger.info(f"Payload: {json.dumps(payload, indent=2)}")
        
        if msg_type == "connection_established":
            client_id = payload.get("clientId")
            logger.info(f"Client ID: {client_id}")
    
    try:
        # Connect to server
        await sio.connect('http://localhost:8080', socketio_path='/ws')
        
        # Wait for connection
        await asyncio.sleep(1)
        
        if not connected:
            logger.error("Failed to connect to server")
            return
        
        # Test 1: Send LLM configuration
        logger.info("\n=== Test 1: Sending LLM configuration ===")
        llm_config = {
            "type": "llm_config",
            "payload": {
                "model": "claude-3.5-sonnet",
                "temperature": 0.8,
                "maxTokens": 2000
            }
        }
        await sio.send(json.dumps(llm_config))
        await asyncio.sleep(1)
        
        # Test 2: Send model selection
        logger.info("\n=== Test 2: Sending model selection ===")
        set_model = {
            "type": "set_model",
            "payload": {
                "model": "gpt-4.1-turbo"
            }
        }
        await sio.send(json.dumps(set_model))
        await asyncio.sleep(1)
        
        # Test 3: Send API key (mock key for testing)
        logger.info("\n=== Test 3: Sending API key ===")
        set_api_key = {
            "type": "set_api_key",
            "payload": {
                "provider": "openai",
                "apiKey": "sk-test-1234567890"
            }
        }
        await sio.send(json.dumps(set_api_key))
        await asyncio.sleep(1)
        
        # Test 4: Send a prompt to verify the model is being used
        logger.info("\n=== Test 4: Sending prompt to test model usage ===")
        prompt = {
            "type": "prompt",
            "payload": {
                "prompt": "Hello, which LLM model are you using?",
                "agentId": "root"
            }
        }
        await sio.send(json.dumps(prompt))
        await asyncio.sleep(3)
        
        logger.info("\n=== All tests completed ===")
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
    finally:
        await sio.disconnect()

if __name__ == "__main__":
    asyncio.run(test_llm_integration())