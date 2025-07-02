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

## **FILE SYSTEM OPERATIONS (WINDOWS)**

### Directory Operations
- `mkdir dirname` – Create directory
- `rmdir dirname` – Remove empty directory (fails if not empty)

### File Operations
- `New-Item -ItemType File -Path filename` – Create empty file (PowerShell)
- `ni filename -ItemType File` – Create empty file (PowerShell short alias)
- `echo some text > filename` – Create file with content
- `del filename` – Delete file
- `copy srcFile destFile` – Copy file
- `move srcFile destFile` – Move/rename file

### Package Management and Project Initialization

**NPM/Node.js:**
- `npm init -y` - Initialize Node.js project with default settings
- `npm install` - Install all dependencies from package.json
- `npm install package-name` - Install and save a package
- `npm install -D package-name` - Install as dev dependency
- `npm run script-name` - Run npm script from package.json
- `npm update` - Update all packages to latest versions
- `npm ci` - Clean install from package-lock.json (faster, reproducible)

## **COMPILATION AND DIAGNOSTICS**
- `node tools/check-typescript.js` - Check TypeScript errors (diagnostics only)
- `node tools/compile-typescript.js` - Compile TypeScript to JavaScript

## **CODE ANALYSIS AND INSPECTION (WINDOWS)**
- `type filename` – Display file contents
- `dir path` – List directory contents
- `find "pattern" filename` - Search for pattern in a file

## **DEVELOPMENT TOOLS**
- `node tools/run-typescript.js src/file.ts` - Run individual TypeScript files
- `node tools/run-tsx.js src/file.ts` - Run TypeScript files with tsx (faster)
- `flake8 path/` - Python linting for directory
- `mypy path/` - Python type checking for directory

## **MASTER AGENT SPECIFIC COMMANDS**

### **PHASE-BASED COMMAND RESTRICTIONS**

**⚠️ PHASE 1 & 2: NO DELEGATION ALLOWED ⚠️**
- **Phase 1 (Product Understanding)**: Use `READ`, `UPDATE_DOCUMENTATION`, `FINISH` only
- **Phase 2 (Structure Stage)**: Use file system commands (`mkdir`, `echo`) and `UPDATE_DOCUMENTATION`
- **Phase 3 (Project Phases)**: Begin using `DELEGATE` to coordinate development

**The DELEGATE command is ONLY available in Phase 3 after structure is created!**

### Project Structure Creation Examples
```bash
# Create a typical web application structure
mkdir src/components
mkdir src/services
mkdir src/types
mkdir src/utils
mkdir test/components
mkdir test/services
mkdir test/integration
mkdir config
mkdir docs
mkdir public

# Create interface and implementation files
New-Item -ItemType File -Path src/types/user.interface.ts
New-Item -ItemType File -Path src/services/auth.ts
New-Item -ItemType File -Path test/services/auth.test.ts

# Initialize development environment
npm init -y
echo {"compilerOptions": {"target": "ES2020"}} > tsconfig.json
```

### Configuration File Creation (Windows PowerShell)
```powershell
# Create package.json with basic structure
@'
{
  "name": "project-name",
  "version": "1.0.0",
  "scripts": {
    "build": "tsc",
    "test": "mocha"
  }
}
'@  | Out-File -Encoding utf8 package.json
```

## **COMMAND USAGE PRINCIPLES**

### Phase 1: Product Understanding
- Use `READ` to understand existing documentation
- Use `UPDATE_DOCUMENTATION` to maintain growing product understanding
- Minimal file operations - focus on clarification

### Phase 2: Structure Stage
- Heavy use of `mkdir` and `echo` to create project architecture
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
- Always verify paths before using destructive commands (`del`)
- Create project structures thoughtfully - they guide all future development

**Safe practices:**
- Use `dir` to verify directory contents before deletion
- Use `mkdir` to create directories.
- Always create backup-friendly structures (avoid deeply nested single-use directories)
- Follow established naming conventions for the technology stack 