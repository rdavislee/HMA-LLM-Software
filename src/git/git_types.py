"""
Git data types for HMA-LLM-Software.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class GitFileStatus(Enum):
    """Git file status enumeration."""
    MODIFIED = "M"
    ADDED = "A"
    DELETED = "D"
    RENAMED = "R"
    COPIED = "C"
    UNMERGED = "U"
    UNTRACKED = "??"
    IGNORED = "!!"


@dataclass
class GitFileChange:
    """Represents a change to a file in git."""
    file_path: str
    status: GitFileStatus
    staged: bool
    old_path: Optional[str] = None  # For renamed files


@dataclass
class GitStatus:
    """Represents the current git status."""
    staged_files: List[GitFileChange]
    unstaged_files: List[GitFileChange]
    untracked_files: List[GitFileChange]
    current_branch: str
    ahead: int  # Commits ahead of remote
    behind: int  # Commits behind remote
    is_dirty: bool  # True if there are uncommitted changes
    is_detached: bool  # True if HEAD is detached


@dataclass
class GitDiff:
    """Represents a git diff for a file."""
    file_path: str
    diff_content: str
    added_lines: int
    removed_lines: int
    is_binary: bool = False


@dataclass
class GitCommit:
    """Represents a git commit."""
    hash: str
    short_hash: str
    author_name: str
    author_email: str
    committer_name: str
    committer_email: str
    message: str
    timestamp: datetime
    parents: List[str]  # Parent commit hashes
    files_changed: List[str]  # List of files changed in this commit


@dataclass
class GitBranch:
    """Represents a git branch."""
    name: str
    is_current: bool
    is_remote: bool
    tracking_branch: Optional[str] = None
    last_commit_hash: Optional[str] = None
    last_commit_message: Optional[str] = None
    last_commit_time: Optional[datetime] = None


@dataclass
class GitUpdate:
    """Represents a git update event."""
    event_type: str  # 'status_changed', 'head_changed', 'branch_changed', etc.
    project_path: str
    data: Dict[str, Any]  # Additional event-specific data
    timestamp: datetime


@dataclass
class GitRemote:
    """Represents a git remote."""
    name: str
    url: str
    fetch_url: str
    push_url: str 