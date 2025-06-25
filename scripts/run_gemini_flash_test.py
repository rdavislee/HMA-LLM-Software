#!/usr/bin/env python
"""Automated testing entry-point using Gemini 2.5 Flash.

This script lets you run the agent hierarchy on a test project using Google's Gemini 2.5 Flash model.
It will:
1. Prompt you for a folder name contained within *test_projects/*.
2. Validate that the folder exists; abort otherwise.
3. Prompt for an initial task description.
4. Spin up the agent hierarchy targeting that directory and use Gemini 2.5 Flash for all LLM calls.
"""

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

    print("\n=== Running agents with Gemini 2.5 Flash – LLM calls will be handled automatically ===\n")
    llm_client = get_llm_client("gemini-2.5-flash")
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