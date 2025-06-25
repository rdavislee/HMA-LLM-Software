### Development Commands
- `python -m pytest tests/` - Run all tests
- `python -m pytest tests/ -v` - Run tests with verbose output
- `python -m pytest tests/ -k "test_name"` - Run specific test
- `python setup.py test` - Run tests using setup.py
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
- `npm audit` - Check for security vulnerabilities
- `npm audit fix` - Fix security vulnerabilities
- `npm outdated` - Check for outdated packages

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
- `npx tsc --noEmit` - TypeScript type checking

### Git Operations
- `git status` - Check repository status
- `git add .` - Stage all changes
- `git commit -m "message"` - Commit changes
- `git push` - Push to remote repository
- `git pull` - Pull from remote repository

### File Operations
- `ls -la` - List all files with details
- `find . -name "*.py"` - Find Python files
- `find . -name "*.js"` - Find JavaScript files
- `find . -name "*.ts"` - Find TypeScript files
- `grep -r "pattern" src/` - Search for pattern in source files
- `cat filename` - Display file contents
- `head -n 10 filename` - Show first 10 lines of file
- `tail -n 10 filename` - Show last 10 lines of file 