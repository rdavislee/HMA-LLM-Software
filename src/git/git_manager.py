"""
Git manager for HMA-LLM-Software.
Handles all git operations using GitPython.
"""

import logging
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime

import git
from git import Repo, InvalidGitRepositoryError, GitCommandError

from .git_types import (
    GitStatus, GitDiff, GitCommit, GitBranch, GitUpdate, GitRemote,
    GitFileChange, GitFileStatus
)

logger = logging.getLogger(__name__)


class GitManager:
    """Manager for git operations within project directories."""
    
    def __init__(self):
        self.repos: Dict[str, Repo] = {}  # Maps project_path to Repo object
        self.watchers: Dict[str, Callable] = {}  # Maps project_path to update callback
        self.last_head_commits: Dict[str, str] = {}  # Track HEAD changes
        self._watch_tasks: Dict[str, asyncio.Task] = {}
    
    def add_project(self, project_path: Path, update_callback: Optional[Callable] = None) -> bool:
        """
        Add a project for git management.
        
        Args:
            project_path: Path to the project directory
            update_callback: Callback function for git updates
            
        Returns:
            True if git repository was found and added, False otherwise
        """
        try:
            repo = Repo(project_path)
            project_key = str(project_path)
            
            self.repos[project_key] = repo
            if update_callback:
                self.watchers[project_key] = update_callback
            
            # Track initial HEAD
            try:
                self.last_head_commits[project_key] = repo.head.commit.hexsha
            except Exception:
                self.last_head_commits[project_key] = ""
            
            # Start watching for changes if callback provided
            if update_callback:
                self._start_watching(project_key)
            
            logger.info(f"Added git repository: {project_path}")
            return True
            
        except InvalidGitRepositoryError:
            logger.warning(f"No git repository found at: {project_path}")
            return False
        except Exception as e:
            logger.error(f"Error adding git repository {project_path}: {e}")
            return False
    
    def remove_project(self, project_path: Path):
        """Remove a project from git management."""
        project_key = str(project_path)
        
        # Stop watching
        if project_key in self._watch_tasks:
            self._watch_tasks[project_key].cancel()
            del self._watch_tasks[project_key]
        
        # Remove from tracking
        self.repos.pop(project_key, None)
        self.watchers.pop(project_key, None)
        self.last_head_commits.pop(project_key, None)
        
        logger.info(f"Removed git repository: {project_path}")
    
    def _start_watching(self, project_key: str):
        """Start watching for git changes in a project."""
        if project_key in self._watch_tasks:
            self._watch_tasks[project_key].cancel()
        
        self._watch_tasks[project_key] = asyncio.create_task(
            self._watch_repo_changes(project_key)
        )
    
    async def _watch_repo_changes(self, project_key: str):
        """Watch for changes in a git repository."""
        try:
            while True:
                await asyncio.sleep(2)  # Check every 2 seconds
                
                repo = self.repos.get(project_key)
                callback = self.watchers.get(project_key)
                
                if not repo or not callback:
                    break
                
                try:
                    # Check if HEAD changed
                    current_head = repo.head.commit.hexsha
                    last_head = self.last_head_commits.get(project_key, "")
                    
                    if current_head != last_head:
                        self.last_head_commits[project_key] = current_head
                        
                        # Emit HEAD change event
                        update = GitUpdate(
                            event_type="head_changed",
                            project_path=project_key,
                            data={"old_head": last_head, "new_head": current_head},
                            timestamp=datetime.now()
                        )
                        
                        await self._safe_callback(callback, update)
                    
                    # Check for status changes (could be optimized)
                    # For now, we'll emit status updates periodically
                    # In a real implementation, we might use file system watchers
                    
                except Exception as e:
                    logger.error(f"Error watching git repo {project_key}: {e}")
                    
        except asyncio.CancelledError:
            pass  # Expected when stopping
        except Exception as e:
            logger.error(f"Unexpected error in git watcher for {project_key}: {e}")
    
    async def _safe_callback(self, callback: Callable, update: GitUpdate):
        """Safely call update callback."""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(update)
            else:
                callback(update)
        except Exception as e:
            logger.error(f"Error in git update callback: {e}")
    
    def get_status(self, project_path: Path) -> Optional[GitStatus]:
        """Get git status for a project."""
        try:
            repo = self.repos.get(str(project_path))
            if not repo:
                return None
            
            # Get current branch
            try:
                current_branch = repo.active_branch.name
                is_detached = False
            except Exception:
                current_branch = "HEAD"
                is_detached = True
            
            # Get file changes
            staged_files = []
            unstaged_files = []
            untracked_files = []
            
            # Parse git status
            status = repo.git.status("--porcelain").split('\n') if repo.git.status("--porcelain") else []
            
            for line in status:
                if not line.strip():
                    continue
                
                status_code = line[:2]
                file_path = line[3:].strip()
                
                # Handle staged changes (first character)
                if status_code[0] != ' ':
                    staged_files.append(GitFileChange(
                        file_path=file_path,
                        status=self._parse_status_code(status_code[0]),
                        staged=True
                    ))
                
                # Handle unstaged changes (second character)
                if status_code[1] != ' ':
                    if status_code[1] == '?':
                        untracked_files.append(GitFileChange(
                            file_path=file_path,
                            status=GitFileStatus.UNTRACKED,
                            staged=False
                        ))
                    else:
                        unstaged_files.append(GitFileChange(
                            file_path=file_path,
                            status=self._parse_status_code(status_code[1]),
                            staged=False
                        ))
            
            # Check ahead/behind status
            ahead, behind = 0, 0
            try:
                if not is_detached and repo.active_branch.tracking_branch():
                    ahead_behind = repo.git.rev_list('--left-right', '--count',
                                                   f'{repo.active_branch.tracking_branch().name}...{current_branch}')
                    behind, ahead = map(int, ahead_behind.split('\t'))
            except Exception:
                pass  # No tracking branch or other error
            
            is_dirty = bool(staged_files or unstaged_files or untracked_files)
            
            return GitStatus(
                staged_files=staged_files,
                unstaged_files=unstaged_files,
                untracked_files=untracked_files,
                current_branch=current_branch,
                ahead=ahead,
                behind=behind,
                is_dirty=is_dirty,
                is_detached=is_detached
            )
            
        except Exception as e:
            logger.error(f"Error getting git status for {project_path}: {e}")
            return None
    
    def _parse_status_code(self, code: str) -> GitFileStatus:
        """Parse git status code to GitFileStatus enum."""
        mapping = {
            'M': GitFileStatus.MODIFIED,
            'A': GitFileStatus.ADDED,
            'D': GitFileStatus.DELETED,
            'R': GitFileStatus.RENAMED,
            'C': GitFileStatus.COPIED,
            'U': GitFileStatus.UNMERGED,
            '?': GitFileStatus.UNTRACKED,
            '!': GitFileStatus.IGNORED
        }
        return mapping.get(code, GitFileStatus.MODIFIED)
    
    def get_diff(self, project_path: Path, file_path: str, staged: bool = False) -> Optional[GitDiff]:
        """Get diff for a specific file."""
        try:
            repo = self.repos.get(str(project_path))
            if not repo:
                return None
            
            if staged:
                # Diff between index and HEAD
                diff_content = repo.git.diff('--cached', file_path)
            else:
                # Diff between working tree and index
                diff_content = repo.git.diff(file_path)
            
            if not diff_content:
                return None
            
            # Count added/removed lines
            added_lines = diff_content.count('\n+') - diff_content.count('\n+++')
            removed_lines = diff_content.count('\n-') - diff_content.count('\n---')
            
            return GitDiff(
                file_path=file_path,
                diff_content=diff_content,
                added_lines=max(0, added_lines),
                removed_lines=max(0, removed_lines),
                is_binary='Binary files' in diff_content
            )
            
        except Exception as e:
            logger.error(f"Error getting git diff for {file_path}: {e}")
            return None
    
    def get_commits(self, project_path: Path, max_count: int = 50) -> List[GitCommit]:
        """Get commit history for a project."""
        try:
            repo = self.repos.get(str(project_path))
            if not repo:
                return []
            
            commits = []
            for commit in repo.iter_commits(max_count=max_count):
                commits.append(GitCommit(
                    hash=commit.hexsha,
                    short_hash=commit.hexsha[:8],
                    author_name=commit.author.name,
                    author_email=commit.author.email,
                    committer_name=commit.committer.name,
                    committer_email=commit.committer.email,
                    message=commit.message.strip(),
                    timestamp=datetime.fromtimestamp(commit.committed_date),
                    parents=[p.hexsha for p in commit.parents],
                    files_changed=list(commit.stats.files.keys())
                ))
            
            return commits
            
        except Exception as e:
            logger.error(f"Error getting git commits for {project_path}: {e}")
            return []
    
    def get_branches(self, project_path: Path) -> List[GitBranch]:
        """Get all branches for a project."""
        try:
            repo = self.repos.get(str(project_path))
            if not repo:
                return []
            
            branches = []
            current_branch_name = repo.active_branch.name if not repo.head.is_detached else None
            
            # Local branches
            for branch in repo.branches:
                is_current = branch.name == current_branch_name
                tracking_branch = None
                
                try:
                    if branch.tracking_branch():
                        tracking_branch = branch.tracking_branch().name
                except Exception:
                    pass
                
                branches.append(GitBranch(
                    name=branch.name,
                    is_current=is_current,
                    is_remote=False,
                    tracking_branch=tracking_branch,
                    last_commit_hash=branch.commit.hexsha,
                    last_commit_message=branch.commit.message.strip(),
                    last_commit_time=datetime.fromtimestamp(branch.commit.committed_date)
                ))
            
            # Remote branches
            for remote in repo.remotes:
                for ref in remote.refs:
                    if ref.name.endswith('/HEAD'):
                        continue
                    
                    branch_name = ref.name
                    branches.append(GitBranch(
                        name=branch_name,
                        is_current=False,
                        is_remote=True,
                        last_commit_hash=ref.commit.hexsha,
                        last_commit_message=ref.commit.message.strip(),
                        last_commit_time=datetime.fromtimestamp(ref.commit.committed_date)
                    ))
            
            return branches
            
        except Exception as e:
            logger.error(f"Error getting git branches for {project_path}: {e}")
            return []
    
    def stage_file(self, project_path: Path, file_path: str) -> bool:
        """Stage a file for commit."""
        try:
            repo = self.repos.get(str(project_path))
            if not repo:
                return False
            
            repo.index.add([file_path])
            return True
            
        except Exception as e:
            logger.error(f"Error staging file {file_path}: {e}")
            return False
    
    def unstage_file(self, project_path: Path, file_path: str) -> bool:
        """Unstage a file."""
        try:
            repo = self.repos.get(str(project_path))
            if not repo:
                return False
            
            repo.index.reset([file_path])
            return True
            
        except Exception as e:
            logger.error(f"Error unstaging file {file_path}: {e}")
            return False
    
    def commit(self, project_path: Path, message: str, author_name: Optional[str] = None, 
               author_email: Optional[str] = None) -> Optional[str]:
        """Create a commit with staged files."""
        try:
            repo = self.repos.get(str(project_path))
            if not repo:
                return None
            
            # Set author if provided
            actor = None
            if author_name and author_email:
                actor = git.Actor(author_name, author_email)
            
            commit = repo.index.commit(message, author=actor, committer=actor)
            return commit.hexsha
            
        except Exception as e:
            logger.error(f"Error creating commit: {e}")
            return None
    
    def create_branch(self, project_path: Path, branch_name: str) -> bool:
        """Create a new branch."""
        try:
            repo = self.repos.get(str(project_path))
            if not repo:
                return False
            
            repo.create_head(branch_name)
            return True
            
        except Exception as e:
            logger.error(f"Error creating branch {branch_name}: {e}")
            return False
    
    def checkout_branch(self, project_path: Path, branch_name: str) -> bool:
        """Checkout a branch."""
        try:
            repo = self.repos.get(str(project_path))
            if not repo:
                return False
            
            repo.git.checkout(branch_name)
            return True
            
        except Exception as e:
            logger.error(f"Error checking out branch {branch_name}: {e}")
            return False
    
    def push(self, project_path: Path, remote_name: str = "origin", 
             branch_name: Optional[str] = None) -> bool:
        """Push commits to remote repository."""
        try:
            repo = self.repos.get(str(project_path))
            if not repo:
                return False
            
            remote = repo.remote(remote_name)
            if branch_name:
                remote.push(branch_name)
            else:
                remote.push()
            
            return True
            
        except Exception as e:
            logger.error(f"Error pushing to remote: {e}")
            return False
    
    def pull(self, project_path: Path, remote_name: str = "origin") -> bool:
        """Pull changes from remote repository."""
        try:
            repo = self.repos.get(str(project_path))
            if not repo:
                return False
            
            remote = repo.remote(remote_name)
            remote.pull()
            return True
            
        except Exception as e:
            logger.error(f"Error pulling from remote: {e}")
            return False
    
    def get_remotes(self, project_path: Path) -> List[GitRemote]:
        """Get all remotes for a project."""
        try:
            repo = self.repos.get(str(project_path))
            if not repo:
                return []
            
            remotes = []
            for remote in repo.remotes:
                urls = list(remote.urls)
                remotes.append(GitRemote(
                    name=remote.name,
                    url=urls[0] if urls else "",
                    fetch_url=urls[0] if urls else "",
                    push_url=urls[0] if urls else ""
                ))
            
            return remotes
            
        except Exception as e:
            logger.error(f"Error getting git remotes for {project_path}: {e}")
            return [] 