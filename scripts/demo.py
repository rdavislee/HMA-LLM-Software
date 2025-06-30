#!/usr/bin/env python3
"""
Demo script for HMA-LLM Software Construction.
Shows how the hierarchical agent system works.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents.manager_agent import ManagerAgent
from agents.coder_agent import CoderAgent
from llm.providers import get_llm_client
from messages.protocol import TaskMessage, Task, MessageType

async def demo_simple_project():
    """Demo creating a simple project with hierarchical agents."""
    print("🎯 HMA-LLM Software Construction Demo")
    print("=" * 50)
    
    # Create a demo project directory
    project_dir = Path("demo_project")
    project_dir.mkdir(exist_ok=True)
    
    print(f"📁 Project directory: {project_dir.absolute()}")
    
    # Initialize LLM client (will use mock if no API keys)
    try:
        llm_client = get_llm_client()
        print("✅ LLM client initialized")
    except Exception as e:
        print(f"⚠️  LLM client error: {e}")
        print("   Using mock responses for demo")
        return
    
    # Create root manager agent
    root_agent = ManagerAgent(
        path=str(project_dir),
        llm_client=llm_client
    )
    
    print("🤖 Root manager agent created")
    
    # Create a task
    task = Task(
        task_id="demo_task_001",
        task_string="Create a simple Python web API with Flask that has a /hello endpoint"
    )
    
    task_message = TaskMessage(
        message_type=MessageType.DELEGATION,
        sender="demo_user",
        recipient=root_agent,
        message_id="demo_msg_001",
        task=task
    )
    
    print(f"📝 Task created: {task.task_string}")
    
    # Activate the agent
    root_agent.activate(task_message)
    print("🚀 Agent activated")
    
    # Process the task
    print("⏳ Processing task...")
    await root_agent.process_task(task.task_string)
    
    print("✅ Task completed!")
    print(f"📁 Check the generated files in: {project_dir.absolute()}")
    
    # Show what was created
    if project_dir.exists():
        print("\n📋 Generated files:")
        for file_path in project_dir.rglob("*"):
            if file_path.is_file():
                print(f"   📄 {file_path.relative_to(project_dir)}")
                if file_path.suffix in ['.py', '.md', '.txt']:
                    try:
                        content = file_path.read_text()[:200]
                        print(f"      Preview: {content}...")
                    except:
                        pass

async def demo_agent_hierarchy():
    """Demo the hierarchical agent structure."""
    print("\n🌳 Agent Hierarchy Demo")
    print("=" * 30)
    
    project_dir = Path("demo_hierarchy")
    project_dir.mkdir(exist_ok=True)
    
    try:
        llm_client = get_llm_client()
    except:
        print("⚠️  Using mock LLM for demo")
        return
    
    # Create manager agent
    manager = ManagerAgent(
        path=str(project_dir),
        llm_client=llm_client
    )
    
    # Create coder agent
    coder = CoderAgent(
        path=str(project_dir / "main.py"),
        parent=manager,
        llm_client=llm_client
    )
    
    # Set up hierarchy
    manager.children = [coder]
    coder.parent = manager
    
    print("🤖 Manager agent created")
    print("👨‍💻 Coder agent created")
    print("🔗 Hierarchy established: Manager -> Coder")
    
    # Show agent capabilities
    print(f"\n📋 Manager capabilities:")
    print(f"   - Manages directory: {manager.scope_path}")
    print(f"   - Personal file: {manager.personal_file}")
    print(f"   - Can delegate tasks: {manager.is_manager}")
    
    print(f"\n📋 Coder capabilities:")
    print(f"   - Manages file: {coder.scope_path}")
    print(f"   - Personal file: {coder.personal_file}")
    print(f"   - Can code: {coder.is_coder}")

def main():
    """Main demo function."""
    print("🎬 Starting HMA-LLM Demo...")
    print()
    
    # Run demos
    asyncio.run(demo_agent_hierarchy())
    print()
    asyncio.run(demo_simple_project())
    
    print("\n🎉 Demo completed!")
    print("\n💡 To see the full system in action:")
    print("   1. Start the backend: python scripts/start_dev.py")
    print("   2. Start the frontend: cd new_frontend && npm run dev")
    print("   3. Open your browser and try creating a project!")

if __name__ == "__main__":
    main() 