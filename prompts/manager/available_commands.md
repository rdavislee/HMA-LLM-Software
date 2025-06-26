# Available Terminal Commands

**IMPORTANT: All terminal commands are executed from the root directory of the project, regardless of which folder the manager agent is responsible for.**

### TypeScript/Node.js (Offline Only)
- `node tools/run-typescript.js src/myfile.ts`     # Run TypeScript files with ts-node
- `node tools/run-tsx.js src/myfile.ts`           # Run TypeScript files with tsx (faster)
- `node tools/compile-typescript.js --outDir dist` # Compile TypeScript to JavaScript
- `node tools/run-mocha.js test/**/*.test.js`     # Run Mocha tests
- `node tools/run-mocha.js --require ts-node/register test/**/*.test.ts` # Run TypeScript tests

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
- `npx eslint src/` - Run ESLint on source files
- `npx prettier --write src/` - Format JavaScript/TypeScript with Prettier

### File Operations
- `ls -la` - List all files with details
- `find . -name "*.py"` - Find Python files
- `find . -name "*.js"` - Find JavaScript files
- `find . -name "*.ts"` - Find TypeScript files
- `grep -r "pattern" src/` - Search for pattern in source files
- `rg "pattern" path/` - Recursively search for pattern in files using ripgrep (rg)
- `cat filename` - Display file contents
- `head -n 10 filename` - Show first 10 lines of file
- `tail -n 10 filename` - Show last 10 lines of file 