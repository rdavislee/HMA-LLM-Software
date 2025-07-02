"""
Configuration constants for the HMA-LLM-Software project.
"""

from enum import Enum
from typing import Optional

# Global Language Configuration
class Language(Enum):
    """Programming language environments supported by the system."""
    TYPESCRIPT = "typescript"
    # Future: PYTHON = "python"

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
    # Default fallback
    return ".py"

# Global constants for allowed terminal commands
ALLOWED_COMMANDS = {
    # Windows-compatible file and directory operations
    'dir',                     # list directory contents
    'type',                    # display file contents
    'find',                    # search within files
    'mkdir',                   # make directory
    'rmdir',                   # remove directory
    'del ',                    # delete file
    'copy ',                   # copy file
    'move ',                   # move/rename file
    'echo ',                   # create/write file via redirection
    'New-Item',                # PowerShell file/directory creation
    'Out-File',                # PowerShell file output
    'ni ',                     # PowerShell alias for New-Item

    # Node & npm (still cross-platform)
    'npm init', 'npm install', 'npm update', 'npm ci', 'npm run',

    # Project-local TypeScript tooling wrappers (Node)
    'node tools/run-typescript.js', 'node tools/run-tsx.js',
    'node tools/compile-typescript.js', 'node tools/run-mocha.js',
    'node tools/run-mocha.cjs', 'node tools/check-typescript.js',

    # Python testing & quality (cross-platform)
    'python -m pytest', 'pytest',
    'python -m unittest', 'python setup.py',
    'python -m py_compile', 'python -c', 'python -m doctest',
    'pip install', 'pip freeze', 'pip list',
    'flake8', 'black', 'isort', 'mypy',

    # Node helper commands
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

# Export public API
__all__ = [
    'Language',
    'set_global_language', 
    'get_global_language',
    'get_language_extension',
    'ALLOWED_COMMANDS',
    'COLLAPSED_DIR_NAMES'
]