# Available Terminal Commands for Managers

**IMPORTANT: All terminal commands are executed from the root directory of the project, regardless of which folder the agent is responsible for.**

## **TESTING RESTRICTIONS**
**⚠️ MANAGER AGENTS CANNOT RUN TESTS DIRECTLY ⚠️**

- **NO direct test execution** - You cannot run `node tools/run-mocha.js` or `python -m pytest`
- **Use tester agents instead** - All testing must be done via `SPAWN tester` commands
- **Compilation only** - You can compile code but not execute tests

**For testing, you MUST:**
1. `SPAWN tester PROMPT="[Broad: Test all files in folder] OR [Specific: Test calculator.ts implementation]"`
2. `WAIT` for tester results
3. Use their findings to guide delegation to child agents

## Compilation and Diagnostics
- `node tools/check-typescript.js` - Check TypeScript errors without compiling (diagnostics only)
- `node tools/compile-typescript.js` - Compile TypeScript to JavaScript (compilation only, no testing)

## Code Analysis
- `flake8 path/` - Python linting for directory
- `mypy path/` - Python type checking for directory

## File Operations (WINDOWS)
- `type filename` - Display file contents
- `find "pattern" filename` - Search for pattern with line numbers
- `dir path` - List directory contents

## Other TypeScript Tools
- `node tools/run-typescript.js src/myfile.ts` - Run individual TypeScript files with ts-node
- `node tools/run-tsx.js src/myfile.ts` - Run individual TypeScript files with tsx (faster) 