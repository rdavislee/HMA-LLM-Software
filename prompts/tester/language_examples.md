Tester Language Examples
Reading Files for Investigation
READ "src/README.md"
READ "src/calculator.ts"
READ "test/calculator.test.ts"
READ "documentation.md"
READ "src/auth/user.py"
READ "test/test_auth.py"
Standard Testing Workflows (90% - NO Scratch Pad)
TypeScript - All Tests Pass
RUN "npm run build"
RUN "npm test"
FINISH PROMPT="All tests passing: 24/24 tests successful. Calculator module fully functional with arithmetic operations, error handling, and precision validation."
TypeScript - Test Failures (Direct Report)
RUN "npm run build"
RUN "npm test"
READ "test/calculator.test.ts"
READ "src/calculator.ts"
READ "documentation.md"
FINISH PROMPT="3 test failures: (1) divide() returns Infinity but test expects Error for division by zero - fix implementation line 45; (2) multiply() precision test expects 1e-10 tolerance but docs specify 1e-8 - fix test assertion; (3) factorial() test exists but not in requirements - remove test."
Python - Mixed Results
RUN "python -m pytest -v"
READ "test/test_auth.py"
READ "src/auth.py"
FINISH PROMPT="5/8 tests failing: (1-3) password validation tests expect min 8 chars but implementation checks 6 - fix implementation line 23; (4) login() test expects dict but function returns tuple - fix test line 45; (5) logout() test checks Redis clearing but Redis not in requirements - remove test."
Java - Compilation Errors
RUN "mvn compile"
READ "src/main/java/UserService.java"
FINISH PROMPT="Compilation failing: 2 errors. (1) UserService.java:15 - Cannot find symbol 'UserRepository', add import; (2) UserService.java:32 - incompatible types String cannot be converted to Long, change userId type to String in method signature."
Specific Test Investigation
Running Targeted Tests
RUN "npm test -- --grep 'authentication'"
RUN "python -m pytest test/test_user.py::test_login -v"
RUN "mvn test -Dtest=CalculatorTest#testDivision"
Code Quality Analysis
RUN "npx eslint src/"
RUN "flake8 src/"
RUN "mypy src/"
FINISH PROMPT="Code quality issues: 12 linting errors (unused imports, line length), 5 missing type annotations in auth.py, no docstrings in 3 public methods. No impact on test failures."
Scratch Pad Usage (10% - ONLY When Explicitly Requested)
TypeScript Deep Debug (Parent explicitly asked)
// Parent: "Debug why parseExpression keeps failing on nested parentheses - I've tried 3 fixes"
RUN "npm test -- --grep 'nested parentheses'"
READ "src/parser.ts"
READ "test/parser.test.ts"

CHANGE CONTENT="""import jwt from 'jsonwebtoken';
import { IAuthService } from './auth.interface';

export class AuthService implements IAuthService {
  async login(email: string, password: string): Promise<string> {
    // Validate credentials
    const user = await this.validateUser(email, password);
    if (!user) throw new Error('Invalid credentials');
    
    // Generate token
    return jwt.sign({ userId: user.id }, process.env.JWT_SECRET);
  }
}"""

RUN "npx tsx scratch_pads/debug_script.ts"
FINISH PROMPT="Deep analysis: parseExpression fails because parenthesis depth counter decrements before recursive call returns. Fix: Move depth-- to after recursive parseExpression call on line 67. Currently decrements at line 65 causing premature depth=0."
Python Deep Debug (Parent explicitly asked)
// Parent: "Debug exact encoding issue in password hash - tried decode('utf-8') and decode('ascii')"
RUN "python -m pytest test/test_auth.py::test_password_hash -v"
READ "src/auth.py"

CHANGE CONTENT="""# Debug encoding - IMPORT ONLY
import sys
sys.path.insert(0, '../src')
from auth import hash_password

password = 'test123'
hashed = hash_password(password)
print(f'Type: {type(hashed)}')
print(f'Value: {hashed}')
print(f'Repr: {repr(hashed)}')

# Test different encodings
for encoding in ['utf-8', 'ascii', 'latin-1']:
    try:
        decoded = hashed.decode(encoding)
        print(f'{encoding}: Success - {decoded[:20]}...')
    except Exception as e:
        print(f'{encoding}: Failed - {e}')"""

RUN "python scratch_pads/debug_script.py"
FINISH PROMPT="Encoding issue resolved: hash_password returns bytes but bcrypt already returns UTF-8 encoded bytes. Issue is test comparing bytes to string. Fix: Change test line 23 from assert result == '$2b$12$...' to assert result.startswith(b'$2b$12$'). No decode needed in implementation."
Multiple Issue Scenarios
Recommend Parallel Testers
RUN "npm test"
READ "test/userSystem.test.ts"
READ "src/auth/login.ts"
READ "src/validation/email.ts"
READ "src/database/connection.ts"
FINISH PROMPT="Found 3 unrelated failure domains: (1) 15 auth tests failing - JWT token malformed; (2) 8 validation tests failing - regex syntax error; (3) 12 database tests failing - connection timeout. Recommend spawning: 'Debug JWT token generation', 'Debug email regex validation', 'Debug database connection timeout'."
Common Reporting Patterns
Implementation Wrong
READ "test/calculator.test.ts"
READ "src/calculator.ts"
FINISH PROMPT="Implementation error: sqrt() throws on negative input but test expects NaN. Fix calculator.ts line 78: replace throw new Error() with return NaN."
Test Wrong
READ "test/user.test.ts"
READ "src/user.ts"
READ "documentation.md"
FINISH PROMPT="Test error: createUser() test expects immediate return but docs specify async operation. Fix test line 34: add await and change to expect(result).resolves.toHaveProperty('id')."
Test Shouldn't Exist
READ "test/advanced.test.ts"
READ "documentation.md"
FINISH PROMPT="Invalid tests: 5 tests for 'advanced mode' features not in requirements. Tests check matrix operations, calculus functions not documented. Remove entire 'Advanced Mathematics' describe block lines 145-289."
Quick Success Patterns
All Pass - TypeScript
RUN "npm run build"
RUN "npm test"
FINISH PROMPT="All tests passing: 45/45 tests successful. User management system fully functional with CRUD operations, authentication, and role-based access control."
All Pass - Python
RUN "python -m pytest -v"
FINISH PROMPT="All tests passing: 32/32 tests successful. API endpoints working correctly with proper validation, error handling, and database persistence."
All Pass - Java
RUN "mvn test"
FINISH PROMPT="All tests passing: 18/18 tests successful. Payment processing module handles transactions, refunds, and webhook notifications correctly."
Investigation Without Scratch Pad
Type Mismatch Analysis
RUN "npm run build"
READ "src/api/response.ts"
READ "test/api.test.ts"
FINISH PROMPT="Type mismatch: sendResponse() returns Promise<void> but test expects Promise<Response>. Implementation correct per interface. Fix test line 67: remove .then(response => expect(response.status))."
Missing Dependency
RUN "python -m pytest -v"
READ "src/service.py"
FINISH PROMPT="Import error: service.py imports 'validate_email' from utils but function not exported. Fix utils.py line 45: add validate_email to __all__ list."
Edge Case Failure
RUN "npm test"
READ "test/parser.test.ts"
READ "src/parser.ts"
FINISH PROMPT="Edge case bug: parseNumber('0.0') returns 0 (number) but parseNumber('.0') returns '.0' (string). Fix parser.ts line 123: add leading zero check for decimal-only inputs."
Key Patterns
90% of work - Direct reporting:
RUN [test command]
READ [relevant files]
FINISH PROMPT="[Specific findings and fixes]"
10% of work - Deep debugging (only when parent explicitly requests):
RUN [test command]
READ [files]
CHANGE CONTENT="// IMPORT ONLY - never copy code\nimport { function } from '../src/file';\n// minimal test code"
RUN [scratch pad]
FINISH PROMPT="[Deep analysis results]"
Never do:

❌ Use scratch pad for routine failures
❌ Copy implementations
❌ Write test suites in scratch pad
❌ Debug without explicit request

Java Deep Debug (Parent explicitly asked)
// Parent: "Debug ConcurrentModificationException in processUsers method"
CHANGE CONTENT="""/* Debugging concurrent modification exception in UserService */
import java.util.*;
import com.example.UserService;

public class UserServiceDebug {
  public static void main(String[] args) {
    UserService service = new UserService();
    List<String> users = new ArrayList<>();
    users.add("alice");
    users.add("bob");
    users.add("charlie");

    try {
      // Attempt to trigger concurrent modification
      service.processUsers(users, user -> {
        if ("bob".equals(user)) {
          users.remove(user);
        }
      });
    } catch (Exception e) {
      e.printStackTrace();
    }

    System.out.println("Final users list:" + users);
  }
}"""

RUN "javac scratch_pads/UserServiceDebug.java && java -cp scratch_pads UserServiceDebug"
FINISH PROMPT="ConcurrentModificationException occurs when removing elements during iteration. Fix processUsers() by using Iterator.remove() or collecting removals in a separate list."