"""
Configuration constants for the HMA-LLM-Software project.
"""

# Global constants for allowed terminal commands
ALLOWED_COMMANDS = {
    # File operations
    'ls', 'dir', 'cat', 'type', 'grep', 'find', 'head', 'tail', 'wc',
    'ripgrep', 'rg',
    
    # Python testing and development
    'python -m pytest', 'python -m unittest', 'python setup.py',
    'pytest',
    'python -m py_compile', 'python -c', 'python -m doctest',
    
    # Python package management
    'pip install', 'pip freeze', 'pip list',
    
    # Python code quality
    'flake8', 'black', 'isort', 'mypy',
    
    # NPM and Node.js (offline wrappers only, project-local tools only)
    'node tools/run-typescript.js', 'node tools/run-tsx.js', 'node tools/compile-typescript.js', 'node tools/run-mocha.js',
    'node tools/run-mocha.cjs', 'node tools/check-typescript.js',
    
    # Node.js development
    'node -e', 'npx eslint', 'npx prettier'
    }

# Directories whose contents should be collapsed in codebase structure views
COLLAPSED_DIR_NAMES = {
    "node_modules",
    "venv",
    ".venv",
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    # Language support directories (do not expose fully in structure views)
    ".node_deps",
    "npm-packages",
    "typescript",
}