### Testing Commands
- `python -m pytest tests/` - Run all tests
- `python -m pytest tests/ -v` - Run tests with verbose output
- `python -m pytest tests/ -k "test_name"` - Run specific test
- `python -m pytest tests/test_file.py::test_function` - Run specific test function
- `python -m unittest discover tests` - Run tests using unittest

### Code Quality
- `flake8 filename.py` - Run linting on specific file
- `black filename.py` - Format code with black
- `isort filename.py` - Sort imports in file
- `mypy filename.py` - Run type checking on file

### File Operations
- `cat filename` - Display file contents
- `head -n 20 filename` - Show first 20 lines of file
- `tail -n 20 filename` - Show last 20 lines of file
- `grep -n "pattern" filename` - Search for pattern with line numbers
- `wc -l filename` - Count lines in file

### Development Tools
- `python -c "import filename; help(filename)"` - Get help on module
- `python -m doctest filename.py` - Run doctests in file
- `python -m py_compile filename.py` - Check syntax without executing 