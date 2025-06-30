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

### Simple Debugging Script
CHANGE CONTENT = "# Debug authentication issue\nimport sys\nsys.path.append('src')\nfrom auth import authenticate_user\n\ndef debug_auth():\n    result = authenticate_user('test@example.com', 'password')\n    print(f\"Auth result: {result}\")\n    print(f\"Type: {type(result)}\")\n    return result\n\nif __name__ == '__main__':\n    debug_auth()\n"

### TypeScript Debugging
CHANGE CONTENT = "// Debug TypeScript compilation issue\nimport { UserController } from '../src/api/userController';\n\nfunction debugUserController() {\n    const controller = new UserController();\n    console.log('Controller created:', controller);\n    \n    try {\n        const result = controller.validateUser('test@example.com');\n        console.log('Validation result:', result);\n    } catch (error) {\n        console.error('Validation error:', error);\n    }\n}\n\ndebugUserController();\n"

### Isolation Testing
CHANGE CONTENT = "# Isolate specific function for testing\ndef test_isolated_function():\n    from src.utils import hash_password\n    \n    test_cases = [\n        ('password123', 'string'),\n        ('', 'empty'),\n        (None, 'none')\n    ]\n    \n    for password, case_type in test_cases:\n        try:\n            result = hash_password(password)\n            print(f\"{case_type}: {type(result)} -> {result}\")\n        except Exception as e:\n            print(f\"{case_type}: ERROR -> {e}\")\n\ntest_isolated_function()\n"

## Complete Diagnostic Workflows

### TypeScript Test Failure Investigation
READ "test/calculator.test.ts"
READ "src/calculator.ts"
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"
CHANGE CONTENT = "// Debug calculator precision issue\nimport { Calculator } from '../src/calculator';\n\nconst calc = new Calculator();\nconst result = calc.multiply(3e100, 1);\nconsole.log('Result:', result);\nconsole.log('Expected:', 3e100);\nconsole.log('Equal?:', result === 3e100);\nconsole.log('Difference:', Math.abs(result - 3e100));\n"
RUN "node tools/run-tsx.js scratch_pads/debug_script.ts"
FINISH PROMPT = "Calculator precision issue: multiply() returns 3.0000000000000002e+100 instead of 3e100. Floating point precision error. Fix: Use Number.parseFloat() or adjust test to use closeTo() with tolerance 1e+90"

### Python Authentication Debugging
READ "src/auth/user.py"
READ "test/test_auth.py"
RUN "python -m pytest test/test_auth.py -v"
CHANGE CONTENT = "# Debug password hashing issue\nimport sys\nsys.path.append('src')\nfrom auth.user import hash_password, verify_password\n\ndef debug_password_flow():\n    password = \"test123\"\n    hashed = hash_password(password)\n    print(f\"Password: {password}\")\n    print(f\"Hashed: {hashed}\")\n    print(f\"Hash type: {type(hashed)}\")\n    \n    verified = verify_password(password, hashed)\n    print(f\"Verification: {verified}\")\n\nif __name__ == \"__main__\":\n    debug_password_flow()\n"
RUN "python scratch_pads/debug_script.py"
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
CHANGE CONTENT = "# Debug import path issues\nimport sys\nprint(\"Python path:\")\nfor p in sys.path:\n    print(f\"  {p}\")\n\ntry:\n    import src.main\n    print(\"✓ src.main imported successfully\")\nexcept ImportError as e:\n    print(f\"✗ src.main failed: {e}\")\n\n# Check if __init__.py exists\nimport os\ninit_files = []\nfor root, dirs, files in os.walk('src'):\n    if '__init__.py' in files:\n        init_files.append(os.path.join(root, '__init__.py'))\n\nprint(f\"__init__.py files found: {len(init_files)}\")\n"
RUN "python scratch_pads/debug_imports.py"
FINISH PROMPT = "Import error: Missing __init__.py in src/utils/ directory. Python treats it as namespace package, breaking relative imports. Fix: Create empty src/utils/__init__.py file"

## Key Investigation Patterns

### Context → Analysis → Debug → Report
1. READ the failing test and implementation
2. RUN tests to see current failures
3. CHANGE scratch pad to create debugging code
4. RUN debugging script to gather data
5. FINISH with detailed findings and recommendations

### Systematic Error Elimination
1. RUN full test suite to see all failures
2. READ related source files
3. CHANGE scratch pad to isolate one component
4. RUN isolated test
5. Repeat until root cause found
6. FINISH with comprehensive analysis 