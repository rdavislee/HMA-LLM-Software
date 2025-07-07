"""
Configuration constants for the HMA-LLM-Software project.
"""

from enum import Enum
from typing import Optional

# Global Language Configuration
class Language(Enum):
    """Programming language environments supported by the system."""
    TYPESCRIPT = "typescript"
    PYTHON = "python"
    JAVA = "java"

# Global language setting
_CURRENT_LANGUAGE: Optional[Language] = None

def set_global_language(language: Language) -> None:
    """Set the global language for the project."""
    global _CURRENT_LANGUAGE
    _CURRENT_LANGUAGE = language

def get_global_language() -> Optional[Language]:
    """Get the current global language."""
    return _CURRENT_LANGUAGE

def get_language_extension(language: Optional[Language] = None) -> str:
    """Get the file extension for the given language (or current global language)."""
    lang = language or _CURRENT_LANGUAGE
    if lang == Language.TYPESCRIPT:
        return ".ts"
    elif lang == Language.JAVA:
        return ".java"  
    elif lang == Language.PYTHON:
        return ".py"
    else:
        raise ValueError(f"Unsupported language: {lang}")

# Global constants for allowed terminal commands (for manager, coder, and ephemeral agents only)
ALLOWED_COMMANDS = {
    # TypeScript/Node test and run
    'npm run',
    'npm test',
    'npm start',
    'node',
    # Python test and run
    'python',
    'pytest',
    'python setup.py',
    'python -c',
    'python -m doctest',
    # Linting/formatting (optional, for code quality)
    'flake8',
    'black',
    'isort',
    'mypy'
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

# Export public API
__all__ = [
    'Language',
    'set_global_language', 
    'get_global_language',
    'get_language_extension',
    'ALLOWED_COMMANDS',
    'COLLAPSED_DIR_NAMES'
]