# Calculus Project

This project implements symbolic calculus operations including expression parsing, evaluation, differentiation, and integration.

Directory Contents
Files

.mocharc.json - [COMPLETE] Mocha configuration file
package-lock.json - [COMPLETE] npm package lock file
package.json - [COMPLETE] npm package manifest
tsconfig.json - [COMPLETE] TypeScript configuration file
interactive_calculator.ts - [NOT STARTED] Interactive calculator application
calculus_README.md - [COMPLETE] This file

Subdirectories

.node_deps/ - [COMPLETE] Node.js dependencies for agent tools
dist/ - [COMPLETE] Compiled JavaScript output
node_modules/ - [COMPLETE] Project dependencies
npm-packages/ - [NOT STARTED] Placeholder for future npm packages
scratch_pads/ - [NOT STARTED] Personal scratchpad for agents
src/ - [IN PROGRESS] Source code for calculus operations, U-substitution functionality added to utils.ts, but experiencing valid compilation errors related to `variable('u')` usage.
test/ - [TESTS ONLY] Test suite for the project, U-substitution tests are in place.
tools/ - [COMPLETE] Utility scripts and tools

Status
Core calculus functions (evaluate, derivate, integrate definite, integrate indefinite) in src/expression.ts and src/utils.ts now include U-substitution. U-substitution integral tests are in test/utils.test.ts. The implementation logic is experiencing valid TS2349 compilation errors in src/utils.ts related to `variable('u')` being incorrectly used as a callable function (it's a String type). This needs to be fixed by the src agent.