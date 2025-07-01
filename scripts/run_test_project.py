#!/usr/bin/env python
"""Automated testing entry-point for running agent hierarchy on test projects.

This script lets you run the agent hierarchy on a test project using a configurable LLM.
It will:
1. Prompt you for a folder name contained within *test_projects/*.
2. Validate that the folder exists; abort otherwise.
3. Prompt for an initial task description.
4. Spin up the agent hierarchy targeting that directory and use the specified LLM for all calls.
"""

# Configure which LLM model to use for testing
# Available options: "gpt-4o", "gpt-4.1", "o3", "o3-pro", "claude-sonnet-4", "claude-opus-4", 
# "claude-3.7-sonnet", "claude-3.5-sonnet", "gemini-2.5-flash", "gemini-2.5-pro", 
# "deepseek-v3", "deepseek-r1", "grok-3", "grok-3-mini", "console"
LLM_MODEL = "gemini-2.5-flash"

import sys
from pathlib import Path

# Add the project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.initializer import initialize_and_run
from src.llm.providers import get_llm_client

def choose_project() -> Path:
    """Ask the user for a folder inside test_projects and return its Path."""
    root = Path(__file__).resolve().parent.parent  # project root (workspace)
    test_projects_dir = root / "test_projects"

    while True:
        name = input(f"Enter the name of the test project directory inside '{test_projects_dir}': ").strip()
        if not name:
            print("Please provide a non-empty folder name. Ctrl-C to abort.")
            continue
        candidate = test_projects_dir / name
        if not candidate.exists() or not candidate.is_dir():
            print(f"Folder '{name}' does not exist under {test_projects_dir}. Aborting.")
            sys.exit(1)
        return candidate

def main() -> None:
    project_path = choose_project()
    initial_prompt = input("Enter the initial prompt/task for the root manager: ").strip()
    if not initial_prompt:
        print("Initial prompt cannot be empty.")
        sys.exit(1)

    print(f"\n=== Running agents with {LLM_MODEL} – LLM calls will be handled automatically ===\n")
    llm_client = get_llm_client(LLM_MODEL)
    result = initialize_and_run(
        project_path,
        initial_prompt,
        llm_client=llm_client,
    )
    print("\n=== Final result from root agent ===")
    print(result)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Goodbye!")
        sys.exit(130) 