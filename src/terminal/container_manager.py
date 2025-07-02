"""
Docker container manager for secure, isolated workspaces.
"""

import asyncio
import logging
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Dict, Optional, Set, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

import docker
from docker.models.containers import Container
from docker.errors import DockerException, APIError

logger = logging.getLogger(__name__)

@dataclass
class ContainerConfig:
    """Configuration for a workspace container."""
    image: str = "node:18-alpine"
    memory_limit: str = "512m"
    cpu_quota: int = 50000  # 0.5 CPU
    cpu_period: int = 100000
    network_mode: str = "none"  # No network access by default
    read_only: bool = False
    user: str = "1000:1000"  # Non-root user
    working_dir: str = "/workspace"
    idle_timeout: int = 1800  # 30 minutes

class ContainerManager:
    """Manages Docker containers for isolated development environments."""
    
    def __init__(self):
        self.containers: Dict[str, Any] = {}
        self.workspaces: Dict[str, Path] = {}
        self.activity_tracker: Dict[str, datetime] = {}
        self.cleanup_task: Optional[asyncio.Task] = None
        self.docker_available = False
        
        try:
            # Try to initialize Docker client
            import docker
            if os.name == 'nt':  # Windows
                # Try different connection methods for Windows
                try:
                    self.docker_client = docker.from_env()
                    # Test connection
                    self.docker_client.ping()
                    self.docker_available = True
                    logger.info("Docker client initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to connect via from_env: {e}")
                    try:
                        # Try named pipe for Windows
                        self.docker_client = docker.DockerClient(base_url='npipe:////./pipe/docker_engine')
                        self.docker_client.ping()
                        self.docker_available = True
                        logger.info("Docker client initialized via named pipe")
                    except Exception as e2:
                        logger.warning(f"Failed to connect via named pipe: {e2}")
                        self.docker_available = False
            else:
                # Unix systems
                self.docker_client = docker.from_env()
                self.docker_client.ping()
                self.docker_available = True
                logger.info("Docker client initialized successfully")
                
        except Exception as e:
            logger.warning(f"Docker not available, using mock mode: {e}")
            self.docker_available = False
            self.docker_client = None

    def is_docker_available(self) -> bool:
        """Check if Docker is available."""
        return self.docker_available

    def create_workspace_directory(self, project_id: str) -> Path:
        """Create workspace directory for a project."""
        workspace_root = Path(__file__).parent.parent.parent / "generated_projects"
        workspace_root.mkdir(exist_ok=True)
        
        workspace_path = workspace_root / f"project_{project_id}"
        workspace_path.mkdir(exist_ok=True)
        
        # Create basic project structure
        (workspace_path / "src").mkdir(exist_ok=True)
        (workspace_path / "README.md").write_text(f"# Project {project_id}\n\nGenerated workspace.\n")
        
        self.workspaces[project_id] = workspace_path
        logger.info(f"Created workspace directory: {workspace_path}")
        return workspace_path

    def create_workspace_container(self, project_id: str, workspace_path: Path) -> str:
        """Create a container for the workspace."""
        if not self.docker_available:
            # Mock container ID
            container_id = f"mock_container_{project_id}_{int(time.time())}"
            self.containers[project_id] = MockContainer(container_id, workspace_path)
            logger.info(f"Created mock container: {container_id}")
            return container_id
            
        try:
            # Convert Windows path to Unix-style for Docker
            host_path = str(workspace_path).replace('\\', '/')
            
            container = self.docker_client.containers.create(
                image="ubuntu:22.04",
                command=["/bin/bash"],
                stdin_open=True,
                tty=True,
                volumes={
                    host_path: {
                        'bind': '/workspace',
                        'mode': 'rw'
                    }
                },
                working_dir='/workspace',
                environment={
                    'DEBIAN_FRONTEND': 'noninteractive',
                    'HOME': '/root',
                    'SHELL': '/bin/bash',
                    'TERM': 'xterm-256color'
                },
                # Security hardening
                user='1000:1000',  # Non-root user
                cap_drop=['ALL'],  # Drop all capabilities
                cap_add=['CHOWN', 'DAC_OVERRIDE', 'FOWNER', 'SETGID', 'SETUID'],  # Minimal required caps
                security_opt=['no-new-privileges:true'],
                mem_limit='512m',  # 512MB memory limit
                cpus=0.5,  # 0.5 CPU cores
                network_mode='none',  # No network access for security
                read_only=False,  # Allow writes to workspace
                tmpfs={
                    '/tmp': 'rw,noexec,nosuid,size=100m',
                    '/var/tmp': 'rw,noexec,nosuid,size=50m'
                },
                name=f"hive_workspace_{project_id}"
            )
            
            self.containers[project_id] = container
            self.update_activity(project_id)
            
            logger.info(f"Created container {container.id} for project {project_id}")
            return container.id
            
        except Exception as e:
            logger.error(f"Failed to create container for project {project_id}: {e}")
            raise

    def start_container(self, project_id: str) -> bool:
        """Start a container."""
        container = self.containers.get(project_id)
        if not container:
            logger.error(f"No container found for project {project_id}")
            return False
            
        if not self.docker_available:
            # Mock container always starts successfully
            return True
            
        try:
            container.start()
            
            # Wait for container to be ready
            for _ in range(10):  # 10 second timeout
                container.reload()
                if container.status == 'running':
                    break
                time.sleep(1)
            else:
                logger.error(f"Container {container.id} failed to start within timeout")
                return False
            
            # Set up the development environment
            self._setup_container_environment(container)
            
            self.update_activity(project_id)
            logger.info(f"Started container {container.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start container for project {project_id}: {e}")
            return False

    def _setup_container_environment(self, container):
        """Set up the development environment inside the container."""
        if not self.docker_available:
            return
            
        try:
            # Install basic development tools
            setup_commands = [
                "apt-get update -q",
                "apt-get install -y -q curl wget git build-essential python3 python3-pip nodejs npm openjdk-11-jdk",
                "npm install -g typescript ts-node",
                "pip3 install --upgrade pip",
                "echo 'export PATH=$PATH:/usr/local/bin' >> /root/.bashrc",
                "echo 'cd /workspace' >> /root/.bashrc"
            ]
            
            for cmd in setup_commands:
                try:
                    result = container.exec_run(cmd, user='root')
                    if result.exit_code != 0:
                        logger.warning(f"Setup command failed: {cmd} (exit code: {result.exit_code})")
                except Exception as e:
                    logger.warning(f"Failed to execute setup command '{cmd}': {e}")
                    
        except Exception as e:
            logger.warning(f"Failed to set up container environment: {e}")

    def get_container(self, project_id: str):
        """Get container for a project."""
        return self.containers.get(project_id)

    def stop_container(self, project_id: str) -> bool:
        """Stop a container."""
        container = self.containers.get(project_id)
        if not container:
            return False
            
        if not self.docker_available:
            # Mock container can always be stopped
            return True
            
        try:
            container.stop(timeout=10)
            logger.info(f"Stopped container for project {project_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop container for project {project_id}: {e}")
            return False

    def remove_container(self, project_id: str) -> bool:
        """Remove a container."""
        container = self.containers.get(project_id)
        if not container:
            return False
            
        if not self.docker_available:
            # Remove from mock containers
            del self.containers[project_id]
            return True
            
        try:
            if container.status == 'running':
                container.stop(timeout=10)
            container.remove()
            del self.containers[project_id]
            logger.info(f"Removed container for project {project_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove container for project {project_id}: {e}")
            return False

    def update_activity(self, project_id: str):
        """Update last activity time for a project."""
        self.activity_tracker[project_id] = datetime.now()

    async def start_cleanup_task(self):
        """Start the cleanup task for idle containers."""
        if self.cleanup_task:
            return
            
        self.cleanup_task = asyncio.create_task(self._cleanup_idle_containers())

    async def _cleanup_idle_containers(self):
        """Periodically clean up idle containers."""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                now = datetime.now()
                idle_threshold = timedelta(minutes=30)  # 30 minutes of inactivity
                
                idle_projects = []
                for project_id, last_activity in self.activity_tracker.items():
                    if now - last_activity > idle_threshold:
                        idle_projects.append(project_id)
                
                for project_id in idle_projects:
                    logger.info(f"Cleaning up idle container for project {project_id}")
                    self.remove_container(project_id)
                    del self.activity_tracker[project_id]
                    if project_id in self.workspaces:
                        del self.workspaces[project_id]
                        
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")

    async def cleanup_all(self):
        """Clean up all containers and resources."""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Clean up all containers
        for project_id in list(self.containers.keys()):
            self.remove_container(project_id)
        
        self.containers.clear()
        self.workspaces.clear()
        self.activity_tracker.clear()


class MockContainer:
    """Mock container for development when Docker is not available."""
    
    def __init__(self, container_id: str, workspace_path: Path):
        self.id = container_id
        self.workspace_path = workspace_path
        self.status = 'running'
        
    def exec_run(self, cmd: str, **kwargs):
        """Mock exec_run method."""
        return type('ExecResult', (), {'exit_code': 0, 'output': b'Mock execution'})()
        
    def start(self):
        """Mock start method."""
        self.status = 'running'
        
    def stop(self, timeout=10):
        """Mock stop method."""
        self.status = 'stopped'
        
    def remove(self):
        """Mock remove method."""
        self.status = 'removed'
        
    def reload(self):
        """Mock reload method."""
        pass 