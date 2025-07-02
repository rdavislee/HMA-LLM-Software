"""
Terminal session management for container interactions.
"""

import asyncio
import logging
import os
import subprocess
import threading
import queue
import time
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime

import docker
from docker.models.containers import Container

logger = logging.getLogger(__name__)

@dataclass
class TerminalSessionInfo:
    """Information about a terminal session."""
    session_id: str
    project_id: str
    container_id: str
    status: str
    created_at: datetime
    cols: int = 80
    rows: int = 24

class TerminalSession:
    """Manages a PTY session with a Docker container or mock container."""
    
    def __init__(
        self, 
        session_id: str, 
        project_id: str, 
        container,  # Can be Container or MockContainer
        on_data: Optional[Callable[[str, str], None]] = None,
        on_exit: Optional[Callable[[str], None]] = None
    ):
        self.session_id = session_id
        self.project_id = project_id
        self.container = container
        self.on_data = on_data
        self.on_exit = on_exit
        
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.cols = 80
        self.rows = 24
        self.is_mock = hasattr(container, 'workspace_path')  # Check if it's a mock container
        
        # Threading for async I/O
        self._read_thread: Optional[threading.Thread] = None
        self._write_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._input_queue = queue.Queue()
        
    async def start(self) -> bool:
        """Start the terminal session."""
        try:
            if self.is_mock:
                # For mock containers, create a local shell
                if os.name == 'nt':  # Windows
                    # Use cmd.exe on Windows for better compatibility
                    shell_cmd = ["cmd.exe"]
                    cwd = str(self.container.workspace_path)
                    
                    # Create process
                    self.process = subprocess.Popen(
                        shell_cmd,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        cwd=cwd,
                        text=True,
                        bufsize=0,
                        universal_newlines=True
                    )
                else:
                    # Use bash on Unix
                    shell_cmd = ["/bin/bash", "-i"]
                    cwd = str(self.container.workspace_path)
                    
                    self.process = subprocess.Popen(
                        shell_cmd,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        cwd=cwd,
                        text=True,
                        bufsize=0,
                        universal_newlines=True
                    )
                
                # Send a welcome message for mock mode
                if self.on_data:
                    welcome_msg = f"\r\n\x1b[33m[MOCK MODE] Local workspace terminal\x1b[0m\r\n"
                    welcome_msg += f"\x1b[33mWorkspace: {self.container.workspace_path}\x1b[0m\r\n"
                    welcome_msg += f"\x1b[33mNote: This is a local shell (Docker not available)\x1b[0m\r\n\r\n"
                    self.on_data(self.session_id, welcome_msg)
            else:
                # Build docker exec command for real containers
                exec_cmd = [
                    "docker", "exec", "-i", 
                    self.container.id,
                    "/bin/sh"
                ]
                
                # Create process
                self.process = subprocess.Popen(
                    exec_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=0,
                    universal_newlines=True
                )
            
            # Start I/O threads
            self._stop_event.clear()
            self._read_thread = threading.Thread(target=self._read_output, daemon=True)
            self._write_thread = threading.Thread(target=self._write_input, daemon=True)
            self._read_thread.start()
            self._write_thread.start()
            
            self.is_running = True
            mode = "mock" if self.is_mock else "docker"
            logger.info(f"Started terminal session {self.session_id} for project {self.project_id} ({mode} mode)")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start terminal session {self.session_id}: {e}")
            return False
    
    def write(self, data: str):
        """Write data to the terminal."""
        if self.is_running:
            try:
                self._input_queue.put(data)
            except Exception as e:
                logger.error(f"Failed to queue input for terminal {self.session_id}: {e}")
    
    def resize(self, cols: int, rows: int):
        """Resize the terminal."""
        self.cols = cols
        self.rows = rows
        logger.debug(f"Terminal {self.session_id} resize to {cols}x{rows} (mock mode doesn't support resize)")
    
    def stop(self):
        """Stop the terminal session."""
        if not self.is_running:
            return
            
        self.is_running = False
        self._stop_event.set()
        
        # Stop the process
        if self.process:
            try:
                self.process.terminate()
                # Wait a bit for graceful shutdown
                try:
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.process.kill()
            except Exception as e:
                logger.error(f"Error terminating process for session {self.session_id}: {e}")
        
        # Wait for threads to finish
        if self._read_thread and self._read_thread.is_alive():
            self._read_thread.join(timeout=2.0)
        if self._write_thread and self._write_thread.is_alive():
            self._write_thread.join(timeout=2.0)
        
        mode = "mock" if self.is_mock else "docker"
        logger.info(f"Stopped terminal session {self.session_id} ({mode} mode)")
        
        # Notify exit
        if self.on_exit:
            try:
                self.on_exit(self.session_id)
            except Exception as e:
                logger.error(f"Error in exit callback for session {self.session_id}: {e}")
    
    def _read_output(self):
        """Read output from the terminal process."""
        buffer = ""
        
        while not self._stop_event.is_set() and self.process and self.process.poll() is None:
            try:
                if self.process.stdout and self.process.stdout.readable():
                    # Read one character at a time to be responsive
                    char = self.process.stdout.read(1)
                    if char:
                        buffer += char
                        
                        # Send data when we have a reasonable chunk or newline
                        if len(buffer) >= 64 or '\n' in buffer or '\r' in buffer:
                            if self.on_data and buffer:
                                self.on_data(self.session_id, buffer)
                            buffer = ""
                    else:
                        # Small delay to prevent busy waiting
                        time.sleep(0.01)
                else:
                    time.sleep(0.01)
                        
            except Exception as e:
                logger.error(f"Error reading from terminal {self.session_id}: {e}")
                break
        
        # Send any remaining buffered data
        if buffer and self.on_data:
            self.on_data(self.session_id, buffer)
        
        # Mark as not running
        self.is_running = False
        
        logger.debug(f"Read thread ended for terminal session {self.session_id}")
    
    def _write_input(self):
        """Write input to the terminal process."""
        while not self._stop_event.is_set():
            try:
                # Get input with timeout to allow checking stop event
                try:
                    data = self._input_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                if self.process and self.process.stdin and self.process.poll() is None:
                    self.process.stdin.write(data)
                    self.process.stdin.flush()
                
                self._input_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error writing to terminal {self.session_id}: {e}")
                break
        
        logger.debug(f"Write thread ended for terminal session {self.session_id}")

class TerminalManager:
    """Manages multiple terminal sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, TerminalSession] = {}
        self.session_info: Dict[str, TerminalSessionInfo] = {}
    
    async def create_session(
        self,
        session_id: str,
        project_id: str,
        container,  # Can be Container or MockContainer
        on_data: Optional[Callable[[str, str], None]] = None,
        on_exit: Optional[Callable[[str], None]] = None
    ) -> bool:
        """Create a new terminal session."""
        if session_id in self.sessions:
            logger.warning(f"Terminal session {session_id} already exists")
            return False
        
        try:
            # Create session
            session = TerminalSession(
                session_id=session_id,
                project_id=project_id,
                container=container,
                on_data=on_data,
                on_exit=on_exit
            )
            
            # Start the session
            success = await session.start()
            if success:
                self.sessions[session_id] = session
                
                # Create session info
                container_id = getattr(container, 'id', 'mock')
                self.session_info[session_id] = TerminalSessionInfo(
                    session_id=session_id,
                    project_id=project_id,
                    container_id=container_id,
                    status='running',
                    created_at=datetime.now()
                )
                
                logger.info(f"Created terminal session {session_id}")
                return True
            else:
                logger.error(f"Failed to start terminal session {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating terminal session {session_id}: {e}")
            return False

    def get_session(self, session_id: str) -> Optional[TerminalSession]:
        """Get a terminal session by ID."""
        return self.sessions.get(session_id)

    def get_session_info(self, session_id: str) -> Optional[TerminalSessionInfo]:
        """Get session info by ID."""
        return self.session_info.get(session_id)

    def write_to_session(self, session_id: str, data: str) -> bool:
        """Write data to a terminal session."""
        session = self.sessions.get(session_id)
        if session and session.is_running:
            session.write(data)
            return True
        return False

    def resize_session(self, session_id: str, cols: int, rows: int) -> bool:
        """Resize a terminal session."""
        session = self.sessions.get(session_id)
        if session:
            session.resize(cols, rows)
            
            # Update session info
            info = self.session_info.get(session_id)
            if info:
                info.cols = cols
                info.rows = rows
            
            return True
        return False

    def close_session(self, session_id: str) -> bool:
        """Close a terminal session."""
        session = self.sessions.get(session_id)
        if session:
            session.stop()
            
            # Clean up
            self.sessions.pop(session_id, None)
            info = self.session_info.pop(session_id, None)
            if info:
                info.status = 'closed'
            
            logger.info(f"Closed terminal session {session_id}")
            return True
        return False

    def get_active_sessions(self) -> Dict[str, TerminalSessionInfo]:
        """Get all active session info."""
        return {sid: info for sid, info in self.session_info.items() if info.status == 'running'}

    def close_all_sessions(self):
        """Close all terminal sessions."""
        for session_id in list(self.sessions.keys()):
            self.close_session(session_id) 