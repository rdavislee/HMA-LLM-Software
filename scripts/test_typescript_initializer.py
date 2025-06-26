#!/usr/bin/env python3
"""
Test script for TypeScript initializer.
- Creates a new test project folder in test_projects/
- Runs the TypeScript initializer for that folder
- Verifies that .node_deps/node_modules/typescript exists in the new project
"""
import os
import shutil
from pathlib import Path
import subprocess
import sys

TEST_PROJECTS = Path(__file__).resolve().parent.parent / "test_projects"
TEST_FOLDER = TEST_PROJECTS / "typescript_init_test"


def main():
    # Clean up any previous test
    if TEST_FOLDER.exists():
        shutil.rmtree(TEST_FOLDER)
    TEST_FOLDER.mkdir(parents=True)

    print(f"Created test project at: {TEST_FOLDER}")

    # Run the typescript initializer for this folder
    result = subprocess.run([
        sys.executable, "scripts/typescript/initializer.py", str(TEST_FOLDER)
    ], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        print("❌ TypeScript initializer failed.")
        sys.exit(1)

    # Check for .node_deps/node_modules/typescript
    typescript_dir = TEST_FOLDER / ".node_deps" / "node_modules" / "typescript"
    if typescript_dir.exists():
        print(f"✅ TypeScript installed at {typescript_dir}")
        sys.exit(0)
    else:
        print(f"❌ TypeScript not found at {typescript_dir}")
        sys.exit(2)


if __name__ == "__main__":
    main() 