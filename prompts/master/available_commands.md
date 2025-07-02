# Available Commands for Master Agent

**IMPORTANT: Master agents have ELEVATED PERMISSIONS for system-level operations. You can create, modify, and delete files and directories throughout the project.**

## **TESTING VIA TESTER AGENTS ONLY**
**⚠️ MASTER AGENTS CANNOT RUN TESTS DIRECTLY ⚠️**

- **NO direct test execution** - You cannot run `node tools/run-mocha.js` or `python -m pytest`
- **Use tester agents instead** - All testing must be done via `SPAWN tester` commands
- **System-wide testing** - Spawn testers for comprehensive project verification

**For testing, you MUST:**
1. `SPAWN tester PROMPT="[System-wide: Test entire project] OR [Component: Test authentication system]"`
2. `WAIT` for tester results
3. Use their findings to guide delegation or structural decisions

## **FILE SYSTEM OPERATIONS (ELEVATED ACCESS)**

### Directory Operations
- `mkdir dirname` - Create single directory
- `mkdir -p path/to/nested/dirs` - Create nested directory structure  
- `rmdir dirname` - Remove empty directory
- `rm -rf dirname` - Remove directory and all contents (USE WITH CAUTION)

### File Operations  
- `touch filename` - Create empty file
- `rm filename` - Delete file
- `cp source destination` - Copy file
- `mv source destination` - Move/rename file
- `echo 'content' > filename` - Create file with content
- `echo 'content' >> filename` - Append content to file

### Project Initialization
- `npm init -y` - Initialize Node.js project
- `npm install package-name` - Install npm packages
- `pip install package-name` - Install Python packages

## **COMPILATION AND DIAGNOSTICS**
- `node tools/check-typescript.js` - Check TypeScript errors (diagnostics only)
- `node tools/compile-typescript.js` - Compile TypeScript to JavaScript

## **CODE ANALYSIS AND INSPECTION**
- `cat filename` - Display file contents (Linux/Mac)
- `type filename` - Display file contents (Windows)
- `head -n 20 filename` - Show first 20 lines of file
- `tail -n 20 filename` - Show last 20 lines of file
- `grep -n "pattern" filename` - Search for pattern with line numbers
- `rg "pattern" path/` - Recursively search for pattern using ripgrep
- `wc -l filename` - Count lines in file
- `ls path/` - List directory contents (Linux/Mac)
- `dir path/` - List directory contents (Windows)
- `find . -name "*.ts"` - Find files by pattern
- `tree` - Display directory tree structure (if available)

## **SYSTEM AND ENVIRONMENT**
- `pwd` - Show current working directory
- `whoami` - Show current user
- `date` - Show current date and time
- `which command` - Show location of command
- `ps aux` - Show running processes (Linux/Mac)
- `tasklist` - Show running processes (Windows)

## **DEVELOPMENT TOOLS**
- `node tools/run-typescript.js src/file.ts` - Run individual TypeScript files
- `node tools/run-tsx.js src/file.ts` - Run TypeScript files with tsx (faster)
- `flake8 path/` - Python linting for directory
- `mypy path/` - Python type checking for directory

## **MASTER AGENT SPECIFIC COMMANDS**

### **PHASE-BASED COMMAND RESTRICTIONS**

**⚠️ PHASE 1 & 2: NO DELEGATION ALLOWED ⚠️**
- **Phase 1 (Product Understanding)**: Use `READ`, `UPDATE_DOCUMENTATION`, `FINISH` only
- **Phase 2 (Structure Stage)**: Use file system commands (`mkdir`, `touch`, `echo`) and `UPDATE_DOCUMENTATION`
- **Phase 3 (Project Phases)**: Begin using `DELEGATE` to coordinate development

**The DELEGATE command is ONLY available in Phase 3 after structure is created!**

### Project Structure Creation Examples
```bash
# Create a typical web application structure
mkdir -p src/components src/services src/types src/utils
mkdir -p test/components test/services test/integration  
mkdir -p config docs public

# Create interface and implementation files
touch src/types/user.interface.ts
touch src/services/auth.ts
touch test/services/auth.test.ts

# Initialize development environment
npm init -y
echo '{"compilerOptions": {"target": "ES2020"}}' > tsconfig.json
```

### Configuration File Creation
```bash
# Create package.json with basic structure
echo '{
  "name": "project-name",
  "version": "1.0.0",
  "scripts": {
    "build": "tsc",
    "test": "mocha"
  }
}' > package.json

# Create README structure
echo '# Project Name

## Overview
[Project description]

## Setup
[Installation instructions]
' > README.md
```

## **COMMAND USAGE PRINCIPLES**

### Phase 1: Product Understanding
- Use `READ` to understand existing documentation
- Use `UPDATE_DOCUMENTATION` to maintain growing product understanding
- Minimal file operations - focus on clarification

### Phase 2: Structure Stage
- Heavy use of `mkdir` and `touch` to create project architecture
- Create configuration files with `echo` and `>` redirection
- Set up package management and build tools
- Establish testing framework structure

### Phase 3: Project Phases  
- Monitor with `SPAWN tester` for system verification
- Use `READ` to verify delegation results
- Update documentation with phase outcomes
- Minimal direct file operations - delegate implementation work

## **SECURITY AND BEST PRACTICES**

⚠️ **ELEVATED PRIVILEGES WARNING** ⚠️
- You have full file system access - use responsibly
- Always verify paths before using destructive commands (`rm -rf`)
- Create project structures thoughtfully - they guide all future development
- Test commands in documentation before using destructive operations

**Safe practices:**
- Use `ls` or `dir` to verify directory contents before deletion
- Use `mkdir -p` instead of multiple `mkdir` commands for nested structures
- Always create backup-friendly structures (avoid deeply nested single-use directories)
- Follow established naming conventions for the technology stack 