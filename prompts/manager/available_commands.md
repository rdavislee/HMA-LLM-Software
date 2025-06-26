# Available Terminal Commands for Managers

**IMPORTANT: All terminal commands are executed from the root directory of the project, regardless of which folder the agent is responsible for.**

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

# 3. If tests fail, delegate fixes to child agents and repeat steps 1-2
```

### **Troubleshooting Test Issues:**
- **"Cannot find files matching pattern"** → You forgot to compile first! Run `node tools/compile-typescript.js`
- **"Module not found"** → Delegate to child coder agent to check import paths
- **"Syntax error"** → Check TypeScript compilation output for errors

### **DO NOT use these unreliable approaches:**
- ❌ `node tools/run-mocha.js test/**/*.test.ts` (TypeScript files directly)
- ❌ `node tools/run-mocha.js --require ts-node/register test/**/*.test.ts` (Complex setup)
- ❌ Running tests without compiling first

### TypeScript Diagnostics (Debugging Errors)
```bash
node tools/check-typescript.js
```
**Use this when you see compilation errors!** This shows detailed TypeScript diagnostics (equivalent to IDE "red squiggles") without compiling. Perfect for diagnosing issues before delegating fixes to child agents.

### Other TypeScript Tools
- `node tools/run-typescript.js src/myfile.ts`     # Run individual TypeScript files with ts-node
- `node tools/run-tsx.js src/myfile.ts`           # Run individual TypeScript files with tsx (faster)

## File Operations
- `cat filename` - Display file contents (Linux/Mac) 
- `type filename` - Display file contents (Windows)
- `head -n 20 filename` - Show first 20 lines of file
- `tail -n 20 filename` - Show last 20 lines of file
- `grep -n "pattern" filename` - Search for pattern with line numbers
- `rg "pattern" path/` - Recursively search for pattern in files using ripgrep
- `wc -l filename` - Count lines in file
- `ls path/` - List directory contents (Linux/Mac)
- `dir path/` - List directory contents (Windows) 