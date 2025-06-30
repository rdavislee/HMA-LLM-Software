# Available Terminal Commands for Tester Agents

**IMPORTANT: All terminal commands are executed from the root directory of the project, regardless of which agent spawned the tester.**

## TypeScript Development Workflow

### **CRITICAL: TypeScript projects require a two-step testing process:**

#### Step 1: Compile TypeScript to JavaScript
```bash
node tools/compile-typescript.js
```
**This MUST be run first!** It compiles all `.ts` files in `src/` and `test/` to JavaScript in the `dist/` directory.

#### Step 2: Run Tests on Compiled JavaScript  
```bash
node tools/run-mocha.js
```
**Only run this AFTER compilation!** This runs tests on the compiled `.js` files in `dist/test/`.

### **Complete Testing Workflow Example:**
```bash
# 1. First, always compile TypeScript
node tools/compile-typescript.js

# 2. Then run the tests  
node tools/run-mocha.js

# 3. If tests fail, investigate with scratch pad debugging and repeat steps 1-2
```

### **Troubleshooting Test Issues:**
- **"Cannot find files matching pattern"** → You forgot to compile first! Run `node tools/compile-typescript.js`
- **"Module not found"** → Check import paths in TypeScript files
- **"Syntax error"** → Check TypeScript compilation output for errors

### **DO NOT use these unreliable approaches:**
- ❌ `node tools/run-mocha.js test/**/*.test.ts` (TypeScript files directly)
- ❌ `node tools/run-mocha.js --require ts-node/register test/**/*.test.ts` (Complex setup)
- ❌ Running tests without compiling first

### TypeScript Diagnostics (Debugging Errors)
```bash
node tools/check-typescript.js
```
**Use this when you see compilation errors!** This shows detailed TypeScript diagnostics (equivalent to IDE "red squiggles") without compiling. Perfect for diagnosing issues before testing.

### Other TypeScript Tools
- `node tools/run-typescript.js src/myfile.ts`     # Run individual TypeScript files with ts-node
- `node tools/run-tsx.js src/myfile.ts`           # Run individual TypeScript files with tsx (faster)
- `node tools/run-tsx.js scratch_pads/debug.ts`   # Run your scratch pad debugging code

## Python Testing and Analysis
- `python -m pytest -v` - Run all tests with verbose output
- `python -m pytest path/to/test.py::test_name -v` - Run specific test
- `python -m pytest --cov=src --cov-report=term` - Run tests with coverage
- `python scratch_pads/debug_scratch_0.py` - Run your scratch pad debugging code
- `flake8 src/` - Python style checking
- `mypy src/` - Python static type analysis

## File Operations
- `cat filename` - Display file contents (Linux/Mac) 
- `type filename` - Display file contents (Windows)
- `head -n 20 filename` - Show first 20 lines of file
- `tail -n 20 filename` - Show last 20 lines of file
- `grep -n "pattern" filename` - Search for pattern with line numbers
- `rg "pattern" path/` - Recursively search for pattern in files using ripgrep (rg)
- `wc -l filename` - Count lines in file

## Python Debugging and Analysis
```bash
# Static type checking
mypy src/

# Code quality analysis
flake8 src/

# Import analysis
python -c "import sys; print(sys.path)"
```

## Code Quality and Analysis Commands

### **Security Analysis:**
- `bandit -r src/` - Python security linting
- `safety check` - Check for known vulnerabilities

## Performance and Profiling

### **Python Profiling:**
```bash
# Profile a specific script
python -m cProfile -o profile.stats scratch_pads/your_scratch_0.py

# Memory profiling (if memory_profiler installed)
python -m memory_profiler scratch_pads/your_scratch_0.py

# Line profiling (if line_profiler installed)
kernprof -l -v scratch_pads/your_scratch_0.py
```

### **Load Testing:**
```bash
# If your scratch pad creates a load test
python scratch_pads/load_test_scratch_0.py
```

## Dependency and Environment Analysis
```bash
# Python environment info
pip list
pip show package_name
python --version
python -c "import sys; print(sys.version_info)"

# Node.js environment info (if applicable)
node --version
npm list --depth=0
```

## Log and Output Analysis
```bash
# View recent logs (if application generates logs)
tail -f logs/app.log

# Search logs for errors
grep -i "error" logs/*.log

# Count occurrences of patterns
grep -c "pattern" filename
```

## Debugging Helpers
```bash
# Check if ports are in use
netstat -tulpn | grep :8080

# Check running processes
ps aux | grep python

# Environment variables
env | grep -i python
printenv
``` 