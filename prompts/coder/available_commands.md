# Available Terminal Commands

**IMPORTANT: All terminal commands are executed from the root directory of the project, regardless of which file or folder the agent is responsible for.**

## **TESTING RESTRICTIONS**
**⚠️ CODER AGENTS MAY RUN ONE TEST DIRECTLY PER TASK ⚠️**

- **ONE direct test execution allowed per task** - You may run `node tools/run-mocha.js` or `python -m pytest` ONCE before using tester agents
- **After your first direct test run, ALL further testing must use tester agents** - Use `SPAWN tester` for all subsequent test runs, retests, or debugging
- **Compilation is always allowed** - You can compile code as many times as needed, but only one direct test run is permitted

**⚠️ COMPILE-FIX/TEST-FIX LOOP PREVENTION:**
- **After 1 failed direct test or compile attempt**: MANDATORY tester spawn for error analysis or retesting
- **NO repeated direct test or compilation attempts** without tester guidance
- **Example**: `SPAWN tester PROMPT="Analyze test failures in [file] - identify missing dependencies"`

**For testing, you MUST:**
1. You may run ONE direct test (e.g., `node tools/run-mocha.js` or `python -m pytest`) per task
2. After that, use `SPAWN tester PROMPT="Test [specific file or broad scope]"` for all further testing
3. `WAIT` for tester results
4. Use their findings to guide your implementation

**For compilation or test errors, you MUST:**
1. First attempt: Fix obvious syntax/import errors only
2. After any failure: `SPAWN tester PROMPT="Analyze compilation or test errors in [file] - identify missing dependencies"`
3. `WAIT` and follow tester guidance - NO GUESSING

## Compilation and Diagnostics
- `node tools/check-typescript.js` - Check TypeScript errors without compiling (diagnostics only)
- `node tools/compile-typescript.js` - Compile TypeScript to JavaScript (compilation only, no testing)

## Code Analysis
- `flake8 filename` - Python linting (specific file)
- `mypy filename` - Python type checking (specific file)

## File Operations
- `cat filename` - Display file contents (Linux/Mac) 
- `type filename` - Display file contents (Windows)
- `head -n 20 filename` - Show first 20 lines of file
- `tail -n 20 filename` - Show last 20 lines of file
- `grep -n "pattern" filename` - Search for pattern with line numbers
- `rg "pattern" path/` - Recursively search for pattern in files using ripgrep (rg)
- `wc -l filename` - Count lines in file

## Other TypeScript Tools
- `node tools/run-typescript.js src/myfile.ts` - Run individual TypeScript files with ts-node
- `node tools/run-tsx.js src/myfile.ts` - Run individual TypeScript files with tsx (faster) 