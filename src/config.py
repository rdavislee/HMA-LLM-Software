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
    'python -m py_compile', 'python -c', 'python -m doctest',
    
    # Python package management
    'pip install', 'pip freeze', 'pip list',
    
    # Python code quality
    'flake8', 'black', 'isort', 'mypy',
    
    # NPM and Node.js
    'npm install', 'npm uninstall', 'npm update', 'npm list', 'npm run',
    'npm test', 'npm audit', 'npm outdated',
    
    # Node.js development
    'node -e', 'npx eslint', 'npx prettier', 'npx tsc', 'npx ts-node'
    }