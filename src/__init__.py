"""
HMA-LLM Software Construction System
"""

from pathlib import Path

# Set the root directory
ROOT_DIR = Path(__file__).parent.parent

def set_root_dir(path: Path):
    """Set the root directory for the project."""
    global ROOT_DIR
    ROOT_DIR = path

__all__ = ['ROOT_DIR', 'set_root_dir']
