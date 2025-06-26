# Coder Agent Documentation

This directory contains prompts and documentation for coder agents.

## Common Issues and Solutions

### TypeScript Compilation Errors (Red Squiggles)

**Problem**: Agent sees compilation errors but doesn't understand what's wrong

**Root Cause**: TypeScript compiler errors can be cryptic when shown through compilation

**Solution**: Use the TypeScript diagnostics tool first:
1. `RUN "node tools/check-typescript.js"` - Shows detailed error diagnostics
2. Fix the specific errors identified
3. `RUN "node tools/compile-typescript.js"` - Verify compilation works
4. `RUN "node tools/run-mocha.js"` - Run tests

### TypeScript Testing Problems

**Problem**: Agent receives "Cannot find files matching pattern" or similar test runner errors

**Root Cause**: Trying to run tests on TypeScript files directly instead of following the compile-then-test workflow

**Solution**: Always follow this exact sequence:
1. `RUN "node tools/check-typescript.js"` (when debugging errors)
2. `RUN "node tools/compile-typescript.js"`
3. `RUN "node tools/run-mocha.js"`

### Test Environment Setup Issues

**Problem**: Tests work in terminal but fail when agents run them

**Root Cause**: Missing dependencies or incorrect configuration

**Solution**: 
1. Check that `.mocharc.json` exists and is properly configured
2. Verify `package.json` has correct test scripts
3. Ensure all dependencies are installed in `.node_deps/`
4. Always follow the compile-then-test workflow

### Import/Module Resolution Errors

**Problem**: "Module not found" errors during testing

**Root Cause**: Incorrect import paths in TypeScript files

**Solution**:
1. Use relative imports: `import { Calculator } from '../src/calculator'`
2. Ensure file extensions match between .ts source and compiled .js
3. Check `tsconfig.json` for correct module resolution settings

## Files in this Directory

- `agent_role.md` - Core responsibilities and protocols for coder agents
- `available_commands.md` - Complete reference of allowed terminal commands  
- `language_examples.md` - Examples of coder language usage
- `coder_grammar.lark` - Formal grammar specification for coder language

## Testing Workflow Reference

For TypeScript projects, the testing workflow is:

1. **Write/modify TypeScript code**
2. **Compile**: `RUN "node tools/compile-typescript.js"`
3. **Test**: `RUN "node tools/run-mocha.js"`
4. **If compilation or tests fail**: Fix code and repeat steps 2-3
5. **If tests pass**: `FINISH PROMPT="Task completed successfully"`

*Use `RUN "node tools/check-typescript.js"` when you need detailed error diagnostics*

This ensures reliable, predictable testing that agents can follow consistently. 