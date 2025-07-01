# Tester Language Examples

## Reading Files for Investigation
READ "README.md"
READ "src/api/userController.ts"
READ "test/userController.test.ts"
READ "src/utils/validation.py"
READ "config/database.json"

## Running Diagnostic Commands

### TypeScript Testing (Required Sequence)
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"

### Specific Test Investigation
RUN "node tools/check-typescript.js"
RUN "node tools/run-mocha.js --grep 'authentication'"
RUN "node tools/run-tsx.js scratch_pads/debug.ts"

### Python Testing and Analysis
RUN "python -m pytest -v"
RUN "python -m pytest test/test_auth.py::test_login -v"
RUN "python -m pytest --cov=src --cov-report=term"
RUN "flake8 src/"
RUN "mypy src/"

## Scratch Pad Debugging

### ⚠️ CRITICAL: IMPORT ONLY - NEVER RECREATE CODE ⚠️

**CORRECT - Simple Import and Call (Python)**
CHANGE CONTENT = "# Debug authentication issue - IMPORT ONLY\nimport sys\nsys.path.append('../src')\nfrom auth import authenticate_user\n\n# Call the function with test inputs\nresult = authenticate_user('test@example.com', 'password')\nprint(f\"Auth result: {result}\")\nprint(f\"Type: {type(result)}\")\n"

**CORRECT - Simple Import and Call (TypeScript)**
CHANGE CONTENT = "// Debug TypeScript issue - IMPORT ONLY\nimport { UserController } from '../src/api/userController';\n\n// Call the function with test inputs\nconst controller = new UserController();\ntry {\n    const result = controller.validateUser('test@example.com');\n    console.log('Validation result:', result);\n} catch (error) {\n    console.error('Validation error:', error);\n}\n"

**ABSOLUTELY FORBIDDEN - DO NOT DO THIS:**
```
❌ CHANGE CONTENT = "// WRONG - Never copy implementations\nfunction validateUser(email: string) {\n    // 50 lines of copied implementation code...\n}\n// This violates protocol and wastes tokens\n"
```

**ABSOLUTELY FORBIDDEN - DO NOT DO THIS:**
```
❌ CHANGE CONTENT = "# WRONG - Never recreate functions\ndef authenticate_user(email, password):\n    # 30 lines of copied implementation...\n# This is code duplication and forbidden\n"
```

### Simple Isolation Testing (CORRECT)
CHANGE CONTENT = "# Isolate specific function - IMPORT ONLY\nimport sys\nsys.path.append('../src')\nfrom utils import hash_password\n\n# Test with different inputs\ntest_cases = ['password123', '', None]\nfor password in test_cases:\n    try:\n        result = hash_password(password)\n        print(f\"Input: {password} -> Output: {type(result)} {result}\")\n    except Exception as e:\n        print(f\"Input: {password} -> Error: {e}\")\n"

## Complete Diagnostic Workflows

### Efficient Testing (All Tests Pass)
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"
FINISH PROMPT = "All tests passing: 15 tests completed successfully. Calculator module fully functional with proper arithmetic operations, edge case handling, and error validation."

### TypeScript Test Failure Investigation (Only when tests fail)
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"
// Tests fail - now investigate
READ "test/calculator.test.ts"
READ "src/calculator.ts"
CHANGE CONTENT = "// Debug calculator precision - IMPORT ONLY\nimport { Calculator } from '../src/calculator';\n\n// Call existing function with test inputs\nconst calc = new Calculator();\nconst result = calc.multiply(3e100, 1);\nconsole.log('Result:', result);\nconsole.log('Expected:', 3e100);\nconsole.log('Equal?:', result === 3e100);\nconsole.log('Difference:', Math.abs(result - 3e100));\n"
RUN "node tools/run-tsx.js scratch_pads/debug_script.ts"
FINISH PROMPT = "Calculator precision issue: multiply() returns 3.0000000000000002e+100 instead of 3e100. Floating point precision error. Fix: Use Number.parseFloat() or adjust test to use closeTo() with tolerance 1e+90"

### Python Testing (Tests Pass)
RUN "python -m pytest test/test_auth.py -v"
FINISH PROMPT = "All authentication tests passing: 8 tests completed successfully. Password hashing, validation, and user creation working correctly."

### Python Authentication Debugging (Only when tests fail)
RUN "python -m pytest test/test_auth.py -v"
// Tests fail - now investigate  
READ "src/auth/user.py"
READ "test/test_auth.py"
CHANGE CONTENT = "# Debug password hashing - IMPORT ONLY\nimport sys\nsys.path.append('src')\nfrom auth.user import hash_password, verify_password\n\n# Call existing functions with test inputs\npassword = \"test123\"\nhashed = hash_password(password)\nprint(f\"Password: {password}\")\nprint(f\"Hashed: {hashed}\")\nprint(f\"Hash type: {type(hashed)}\")\n\nverified = verify_password(password, hashed)\nprint(f\"Verification: {verified}\")\n"
RUN "python scratch_pads/debug_script_scratch_0.py"
FINISH PROMPT = "Password hashing returns bytes but test expects string. Issue in auth/user.py line 23: bcrypt.hashpw() returns bytes. Fix: add .decode('utf-8') to hash_password() return statement. Also found: no validation for None/empty passwords"

### Code Quality Investigation
READ "src/api/"
RUN "flake8 src/api/"
RUN "mypy src/api/"
RUN "python -m pytest test/test_api.py --cov=src.api --cov-report=term"
FINISH PROMPT = "Code quality analysis: 15 linting errors in src/api/, mostly unused imports and line length. Type checking shows 3 missing type annotations. Test coverage at 78%. Missing tests for error handling in userController.py lines 45-52"

### Import Error Investigation
READ "src/main.py"
READ "test/test_main.py"
RUN "python -m pytest test/test_main.py -v"
CHANGE CONTENT = "# Debug import path issues - ANALYSIS ONLY\nimport sys\nimport os\n\nprint(\"Python path:\")\nfor p in sys.path:\n    print(f\"  {p}\")\n\n# Test importing the problematic module\ntry:\n    import src.main\n    print(\"✓ src.main imported successfully\")\nexcept ImportError as e:\n    print(f\"✗ src.main failed: {e}\")\n\n# Check if __init__.py exists\ninit_files = []\nfor root, dirs, files in os.walk('src'):\n    if '__init__.py' in files:\n        init_files.append(os.path.join(root, '__init__.py'))\n\nprint(f\"__init__.py files found: {len(init_files)}\")\n"
RUN "python scratch_pads/debug_imports_scratch_0.py"
FINISH PROMPT = "Import error: Missing __init__.py in src/utils/ directory. Python treats it as namespace package, breaking relative imports. Fix: Create empty src/utils/__init__.py file"

### Recommending Multiple Testers for Complex Issues
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"
// Many different tests failing across multiple domains
READ "test/userSystem.test.ts"
READ "src/user/auth.ts"
READ "src/user/validation.ts"  
READ "src/user/database.ts"
FINISH PROMPT = "Multiple unrelated failure types detected: 1) Authentication token parsing fails (auth.ts lines 23-45), 2) Email validation regex broken (validation.ts line 67), 3) Database connection timeout errors (database.ts line 89). These are 3 separate problem domains. RECOMMEND: Parent should spawn separate testers for 'Debug authentication token parsing', 'Debug email validation failures', and 'Debug database connection timeouts' for parallel investigation."

## Key Investigation Patterns

### Efficient Success Path (90% of cases)
1. RUN tests immediately  
2. If all pass: FINISH with success summary
3. No scratch pad needed, no extra investigation

### Failure Investigation Path (only when needed)
1. RUN tests to see current failures
2. READ the failing test and implementation
3. **Only if unclear**: CHANGE scratch pad to debug specific failing function
4. RUN debugging script to gather data
5. FINISH with detailed findings and recommendations

### Multiple Issue Decision Path
1. If failures are in ONE domain (e.g., all auth-related): Handle all in current investigation
2. If failures are in MULTIPLE domains (e.g., auth + validation + database): Recommend parent spawn additional testers
3. **Rule of thumb**: More than 2-3 unrelated problem types = recommend multiple testers

### ⚠️ CRITICAL: WHAT IS ABSOLUTELY FORBIDDEN ⚠️

**NEVER DO THESE THINGS:**
- ❌ Copy function implementations into scratch pad
- ❌ Recreate or rewrite existing functions  
- ❌ Write entire function bodies
- ❌ Duplicate any implementation code
- ❌ Write test suites in scratch pad  
- ❌ Use scratch pad when tests are passing
- ❌ Write implementations in scratch pad

**ONLY DO THESE THINGS:**
- ✅ Import functions using proper import statements
- ✅ Call imported functions with test inputs
- ✅ Write minimal console.log/print statements
- ✅ Use scratch pad ONLY to debug failing functions by calling them
- ✅ Write simple variable assignments for test data 