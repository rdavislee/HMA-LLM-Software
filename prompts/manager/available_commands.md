### Development Commands
- `python -m pytest tests/` - Run all tests
- `python -m pytest tests/ -v` - Run tests with verbose output
- `python -m pytest tests/ -k "test_name"` - Run specific test
- `python setup.py test` - Run tests using setup.py
- `python -m unittest discover tests` - Run tests using unittest

### Package Management
- `pip install -r requirements.txt` - Install dependencies
- `pip install package_name` - Install a specific package
- `pip freeze > requirements.txt` - Generate requirements file
- `pip list` - List installed packages

### Build and Installation
- `python setup.py build` - Build the project
- `python setup.py install` - Install the project
- `python setup.py develop` - Install in development mode

### Code Quality
- `flake8 src/` - Run linting
- `black src/` - Format code with black
- `isort src/` - Sort imports
- `mypy src/` - Run type checking

### Git Operations
- `git status` - Check repository status
- `git add .` - Stage all changes
- `git commit -m "message"` - Commit changes
- `git push` - Push to remote repository
- `git pull` - Pull from remote repository

### File Operations
- `ls -la` - List all files with details
- `find . -name "*.py"` - Find Python files
- `grep -r "pattern" src/` - Search for pattern in source files
- `cat filename` - Display file contents
- `head -n 10 filename` - Show first 10 lines of file
- `tail -n 10 filename` - Show last 10 lines of file 