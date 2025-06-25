# Available Terminal Commands

**IMPORTANT: All terminal commands are executed from the root directory of the project, regardless of which file or folder the agent is responsible for.**

### Testing Commands
- `python -m pytest tests/` - Run all tests
- `python -m pytest tests/ -v` - Run tests with verbose output
- `python -m pytest tests/ -k "test_name"` - Run specific test
- `python -m pytest tests/test_file.py::test_function` - Run specific test function
- `python -m unittest discover tests` - Run tests using unittest

### NPM and Node.js Commands
- `npm install` - Install dependencies from package.json
- `npm install package-name` - Install a specific package
- `npm install --save-dev package-name` - Install dev dependency
- `npm uninstall package-name` - Remove a package
- `npm update` - Update all packages
- `npm list` - List installed packages
- `npm run script-name` - Run a script defined in package.json
- `npm test` - Run tests (typically mocha)
- `npm run test:watch` - Run tests in watch mode
- `npm run build` - Build the project
- `npm run dev` - Start development server
- `npm run lint` - Run linting
- `npm run format` - Format code

### Code Quality
- `flake8 filename.py` - Run linting on specific file
- `black filename.py` - Format code with black
- `isort filename.py` - Sort imports in file
- `mypy filename.py` - Run type checking on file
- `npx eslint filename.js` - Run ESLint on JavaScript file
- `npx prettier --write filename.js` - Format JavaScript with Prettier
- `npx tsc --noEmit` - TypeScript type checking

### File Operations
- `cat filename` - Display file contents
- `head -n 20 filename` - Show first 20 lines of file
- `tail -n 20 filename` - Show last 20 lines of file
- `grep -n "pattern" filename` - Search for pattern with line numbers
- `rg "pattern" path/` - Recursively search for pattern in files using ripgrep (rg)
- `wc -l filename` - Count lines in file

### Development Tools
- `python -c "import filename; help(filename)"` - Get help on module
- `python -m doctest filename.py` - Run doctests in file
- `python -m py_compile filename.py` - Check syntax without executing
- `node -e "console.log(require('./filename.js'))"` - Load and log Node.js module
- `npx ts-node filename.ts` - Run TypeScript file directly 