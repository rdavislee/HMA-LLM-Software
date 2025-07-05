#!/usr/bin/env python
"""Manual tester for *initialize_new_project*.

This helper script lets you spin-up **a brand-new** project using the
three-phase workflow driven by the *master* agent.  You will play the role of
the human responder whenever the master agent issues a *FINISH* directive that
requires clarification.

Key characteristics
-------------------
1. Master agent LLM  : **Gemini-2.5-Pro**  (strong reasoning / long context)
2. All other agents  : **Gemini-2.5-Flash** (fast & cheaper)
3. Human interface   : Simple *stdin* prompt for each FINISH turn.

Usage
-----
$ python scripts/run_new_project_manual.py  
… follow the interactive prompts …
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Awaitable

# Make project root importable when script is executed directly
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.initializer import initialize_new_project  # noqa: E402
from src.llm.providers import (  # noqa: E402
    Gemini25ProClient,
    Gemini25FlashClient,
)

# ---------------------------------------------------------------------------
# Human ↔︎ master interface helper
# ---------------------------------------------------------------------------
async def terminal_human_interface(completion_message: str) -> str:  # noqa: D401
    """Print *completion_message* and wait for a human reply on stdin."""
    sep = "\n" + "-" * 80 + "\n"
    print(sep + completion_message + sep)
    return input("[Human] > ")


async def async_main() -> None:
    # ---------------------------------------------------------------------
    # Collect basic input
    # ---------------------------------------------------------------------
    # ------------------------------------------------------------------
    # Choose folder name under ./test_projects
    # ------------------------------------------------------------------
    workspace_root = Path(__file__).resolve().parent.parent  # project root
    test_projects_dir = workspace_root / "test_projects"

    folder_name = input(
        f"Enter the name for the NEW project directory inside '{test_projects_dir}': "
    ).strip()

    if not folder_name:
        print("Folder name cannot be empty; aborting.")
        sys.exit(1)

    root_path = test_projects_dir / folder_name

    if root_path.exists():
        print(f"Folder '{folder_name}' already exists inside {test_projects_dir}. Aborting to prevent overwrite.")
        sys.exit(1)

    initial_prompt = input(
        "Describe, in one sentence, what you would like to build: "
    ).strip()
    if not initial_prompt:
        print("Initial prompt cannot be empty; aborting.")
        sys.exit(1)

    # ---------------------------------------------------------------------
    # Spin-up the system
    # ---------------------------------------------------------------------
    print("\n=== Bootstrapping agents – you will be asked to answer FINISH questions ===\n")

    master_llm = Gemini25ProClient()
    base_llm = Gemini25FlashClient()

    await initialize_new_project(
        root_directory=root_path,
        initial_prompt=initial_prompt,
        human_interface_fn=terminal_human_interface,
        master_llm_client=master_llm,
        base_llm_client=base_llm,
    )

    print("\n🎉  Project scaffolding complete.  Check the directory at:")
    print(f"   {root_path}\n")


def main() -> None:
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\nInterrupted by user – exiting.")
        sys.exit(130)


if __name__ == "__main__":
    main() 