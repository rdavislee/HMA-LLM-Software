#!/usr/bin/env python
"""Manual tester for *initialize_ongoing_project*.

This helper script lets you spin-up the **agent hierarchy for an existing**
project and drive the two-phase workflow (documentation ⟶ change) powered by
`initialize_ongoing_project`.  You will play the role of the human responder
whenever the master agent issues a *FINISH* directive that requires
clarification.

Key characteristics
-------------------
1. Master agent LLM  : **Gemini-2.5-Pro**  (strong reasoning / long context)
2. All other agents  : **Gemini-2.5-Flash** (fast & cheaper)
3. Human interface   : Simple *stdin* prompt for each FINISH turn.

Usage
-----
$ python scripts/run_ongoing_project_manual.py  
… follow the interactive prompts …
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Awaitable

# Make project root importable when script is executed directly
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.initializer import initialize_ongoing_project  # noqa: E402
from src.llm.providers import (  # noqa: E402
    Gemini25ProClient,
    Gemini25FlashClient,
)
from src.config import Language

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
    workspace_root = Path(__file__).resolve().parent.parent  # project root
    test_projects_dir = workspace_root / "test_projects"

    folder_name = input(
        f"Enter the name of the EXISTING project directory inside '{test_projects_dir}': "
    ).strip()

    if not folder_name:
        print("Folder name cannot be empty; aborting.")
        sys.exit(1)

    root_path = test_projects_dir / folder_name

    if not root_path.exists():
        print(
            f"Folder '{folder_name}' does NOT exist inside {test_projects_dir}. Aborting."
        )
        sys.exit(1)

    # ------------------------------------------------------------------
    # Project goal (overall purpose)
    # ------------------------------------------------------------------
    project_goal = input(
        "Describe, in one sentence, your overall goal for this existing project: "
    ).strip()
    if not project_goal:
        print("Project goal cannot be empty; aborting.")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Choose programming language (defaults to typescript)
    # ------------------------------------------------------------------
    language_choice = (
        input(
            "Select the project's primary programming language (python/typescript/java) [typescript]: "
        )
        .strip()
        .lower()
    ) or "typescript"

    valid_languages = {
        "python": Language.PYTHON,
        "typescript": Language.TYPESCRIPT,
        "java": Language.JAVA,
    }

    if language_choice not in valid_languages:
        print(
            f"Unsupported language '{language_choice}'. Must be one of: python, typescript, or java. Aborting."
        )
        sys.exit(1)

    chosen_language = valid_languages[language_choice]

    # ---------------------------------------------------------------------
    # Spin-up the system
    # ---------------------------------------------------------------------
    print("\n=== Bootstrapping agents for existing project – you will be asked to answer FINISH questions ===\n")

    master_llm = Gemini25ProClient()
    base_llm = Gemini25FlashClient()

    await initialize_ongoing_project(
        root_directory=root_path,
        project_goal=project_goal,
        human_interface_fn=terminal_human_interface,
        language=chosen_language,
        master_llm_client=master_llm,
        base_llm_client=base_llm,
    )

    print("\n🎉  Ongoing project initialisation complete.  Review the project directory at:")
    print(f"   {root_path}\n")


def main() -> None:
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\nInterrupted by user – exiting.")
        sys.exit(130)


if __name__ == "__main__":
    main() 