"""
Terminal management for container-backed workspaces.
"""

from .container_manager import ContainerManager
from .terminal_session import TerminalSession

__all__ = ['ContainerManager', 'TerminalSession'] 