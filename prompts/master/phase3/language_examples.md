# Phase 3: Master Language Examples - Implementation

## Core Phase 3 Commands (DELEGATE is Primary)

### Strategic Parallel Delegation Examples

#### Foundation Phase - Maximum Concurrency
```
DELEGATE PROMPT="Phase: Foundation Implementation - Concurrent Development
Documents to read: documentation.md, documents/data_models.md

Implement ALL of the following CONCURRENTLY (these have no interdependencies):

TRACK 1 - Core Interfaces:
- src/interfaces/IUser.ts
- src/interfaces/IProduct.ts  
- src/interfaces/ICart.ts
- src/interfaces/IOrder.ts
- src/interfaces/IPayment.ts

TRACK 2 - Base Models:
- src/models/base.model.ts (abstract base class)
- src/models/audit.model.ts (createdAt, updatedAt)

TRACK 3 - Utilities:
- src/utils/logger.ts
- src/utils/validator.ts
- src/utils/crypto.ts

TRACK 4 - Configuration:
- src/config/database.ts
- src/config/redis.ts
- src/config/environment.ts

Each track should be developed simultaneously. No need to wait for other tracks."
```

#### Service Layer - Parallel with Mocks
```
DELEGATE PROMPT="Phase: Service Implementation - Use Mocks for Parallel Development
Documents: documentation.md, documents/business_logic.md

Implement these service groups CONCURRENTLY:

GROUP A - User Domain (3 developers):
Developer A1: src/services/user.service.ts
Developer A2: src/services/auth.service.ts  
Developer A3: src/services/profile.service.ts

GROUP B - Product Domain (3 developers):
Developer B1: src/services/product.service.ts
Developer B2: src/services/inventory.service.ts
Developer B3: src/services/search.service.ts

GROUP C - Order Domain (3 developers):
Developer C1: src/services/cart.service.ts
Developer C2: src/services/order.service.ts
Developer C3: src/services/payment.service.ts

IMPORTANT: Use the mock implementations in src/mocks/ for any dependencies on other services. This allows true parallel development. We'll integrate real services in the next phase."
```

### API Implementation with Frontend Contract Verification

```
# First, read the API contract
READ file "documents/api_contract.md"
READ file "documents/frontend_description.md"

DELEGATE PROMPT="Phase: API Controller Implementation
Documents: documents/api_contract.md, documents/frontend_description.md
CRITICAL: Frontend integration depends on EXACT response formats.

Implement authentication controllers with these EXACT endpoints:

POST /api/auth/register
Request: { email, password, firstName, lastName }
Response: { success: true, message: 'Check email', userId: 'uuid' }
Errors: { success: false, error: 'EMAIL_EXISTS', message: '...' }

POST /api/auth/login  
Request: { email, password }
Response: { success: true, data: { token, refreshToken, user: {...} } }
Errors: { success: false, error: 'INVALID_CREDENTIALS', message: '...' }

GET /api/auth/me
Headers: { Authorization: 'Bearer token' }
Response: { success: true, data: { user: {...} } }
Errors: { success: false, error: 'UNAUTHORIZED', message: '...' }

IMPORTANT: Every response must have 'success' field. Error responses must include 'error' code."
```

### Handling Agent "Hallucinations"

```
# When agent says they can't delegate
DELEGATE PROMPT="You reported 'I cannot delegate as I don't have that capability.' This is incorrect. You are a manager agent with full delegation capabilities. 

Your role explicitly includes delegating to child agents. Please proceed with the task:
1. Create the necessary file agents for auth.service.ts and user.service.ts
2. Delegate the implementation tasks to them
3. Coordinate their work

This is a core function of your role. Proceed with confidence."

# When agent says task is impossible
DELEGATE PROMPT="You reported the task cannot be completed. This is almost certainly incorrect. Let's break it down:

The error 'Cannot find module @/services/user.service' means:
1. The TypeScript path alias isn't set up correctly
2. OR the file doesn't exist yet

Solution:
1. First, create the file src/services/user.service.ts
2. Check tsconfig.json has the correct path mappings
3. If using Jest, ensure jest.config.js has matching moduleNameMapper

This is a solvable problem. Please implement the solution and continue."
```

### Debugging Persistent Test Failures

```
# Read the failing test
READ file "src/services/auth.service.test.ts"
READ file "src/services/auth.service.ts"

# Specific debugging guidance
DELEGATE PROMPT="Phase: Debug Auth Test Failures
The auth service tests are failing with 'SecretOrPrivateKeyRequired'. Here's the issue:

1. The JWT signing is missing the secret key
2. In auth.service.ts, the signToken method needs: jwt.sign(payload, process.env.JWT_SECRET)
3. In the test file, add to beforeAll: process.env.JWT_SECRET = 'test-secret'

Fix these specific issues and re-run the tests. The tests should pass after these changes."

# After fix attempt
RUN "npm test -- src/services/auth.service.test.ts"

# If still failing
DELEGATE PROMPT="The test is still failing. Let me be more specific:
1. Open src/services/auth.service.ts
2. Find line with: jwt.sign(payload, '', options)
3. Change to: jwt.sign(payload, this.config.jwtSecret, options)
4. Ensure config is properly injected in constructor
5. Re-run tests"
```

### Integration Testing Implementation

```
DELEGATE PROMPT="Phase: Integration Testing
Documents: Read all files in src/controllers/

Create comprehensive integration tests:

1. src/integration/auth-flow.integration.test.ts
   - User registers
   - Email verification (mocked)
   - User logs in
   - Token refresh works
   - Logout invalidates token

2. src/integration/shopping-flow.integration.test.ts  
   - User browses products
   - Adds items to cart
   - Updates quantities
   - Applies discount code
   - Completes checkout
   - Order appears in history

3. src/integration/admin-flow.integration.test.ts
   - Admin logs in
   - Creates new product
   - Updates inventory
   - Views all orders
   - Processes refund

Each test should use the actual service layer, not mocks."
```

### API Testing with Frontend Simulation

```
DELEGATE PROMPT="Phase: Comprehensive API Testing
Documents: documents/api_contract.md, documents/frontend_description.md

Create API tests that exactly simulate frontend behavior:

src/api-tests/auth.api.test.ts:
```typescript
describe('Authentication API - Frontend Simulation', () => {
  it('should handle complete registration flow like frontend', async () => {
    // Frontend sends this exact format
    const response = await request(app)
      .post('/api/auth/register')
      .send({
        email: 'newuser@example.com',
        password: 'SecurePass123!',
        firstName: 'John',
        lastName: 'Doe',
        acceptTerms: true
      });
    
    expect(response.status).toBe(201);
    expect(response.body).toMatchObject({
      success: true,
      message: expect.stringContaining('email'),
      userId: expect.any(String)
    });
  });
});
```

Implement similar tests for ALL endpoints the frontend uses."
```

### Complex Debugging Scenario

```
# Multiple reads to understand the issue
READ file "src/controllers/product.controller.ts"
READ file "src/services/product.service.ts"  
READ file "src/models/product.model.ts"
READ folder "logs"

UPDATE_DOCUMENTATION CONTENT="## Debugging Product Search Issue

Problem: Frontend search returns 500 error

Investigation:
1. Controller properly passes search params to service
2. Service constructs Sequelize query correctly  
3. Model has fulltext index on name and description
4. Error in logs: 'Cannot read property toLowerCase of undefined'

Root Cause: Search term not being validated, undefined passed to query

Solution: Add validation in controller before passing to service"

DELEGATE PROMPT="Fix product search error:
In product.controller.ts, before calling productService.search():
1. Add validation: const searchTerm = req.query.search?.toString() || '';
2. Add minimum length check: if (searchTerm && searchTerm.length < 2) return 400 error
3. Update the API test to verify this validation
4. Ensure the fix doesn't break existing tests"
```

### Performance Optimization Delegation

```
# Check current performance
RUN "npm test -- --testNamePattern='performance'"

DELEGATE PROMPT="Phase: Performance Optimization
The API performance tests show product listing takes 800ms average. Target is <200ms.

Optimize the following:
1. In product.service.ts, add Redis caching for frequently accessed products
2. In product.model.ts, add database indexes on: category_id, price, created_at
3. In product.controller.ts, implement pagination with max limit of 50
4. Add cache invalidation when products are updated

After changes, re-run performance tests to verify <200ms response time."
```

### Final Implementation Verification

```
# Comprehensive verification before completion
READ folder "src/controllers"
READ folder "src/api-tests"
RUN "npm run test:coverage"

UPDATE_DOCUMENTATION CONTENT="## Pre-Completion Verification

API Compliance Check:
✅ All 47 endpoints implemented
✅ Response formats match frontend contract
✅ Error codes consistent across API
✅ Authentication required where specified

Test Coverage:
✅ Unit Tests: 89% coverage
✅ Integration Tests: All user flows covered
✅ API Tests: 156 test cases, all passing

Performance:
✅ Average response time: 127ms
✅ Concurrent user support: Tested 1000 users
✅ Database queries: All using indexes

Remaining Issues: None"

FINISH PROMPT="Implementation Complete! 🎉

All features implemented and tested:
✅ Authentication system with JWT refresh tokens
✅ Product catalog with advanced search and filters  
✅ Shopping cart with real-time inventory checks
✅ Order processing with Stripe payment integration
✅ Admin dashboard with full CRUD operations
✅ Email notifications via SendGrid

Test Results:
- Unit Tests: 89% coverage, 342 tests passing
- Integration Tests: 47 scenarios, all passing
- API Tests: 156 tests, 100% frontend compliant
- Performance: All endpoints <200ms response time

The backend is ready for production deployment. All API contracts are met and comprehensive tests ensure reliability."
```

## Phase 3 Workflow Examples

### Example 1: Complete Service Implementation Flow
```
# Start with planning
UPDATE_DOCUMENTATION CONTENT="## Service Implementation Plan
Implementing 9 services across 3 domains
Estimated time: 3 days with parallel development"

# Delegate foundation
DELEGATE PROMPT="Phase: Foundation - Interfaces and Models
Implement all interfaces first (concurrent), then all models (concurrent).
This creates the contracts for parallel service development."

# Check progress
READ folder "src/interfaces"
READ folder "src/models"

# Delegate services with maximum parallelism
DELEGATE PROMPT="Phase: Service Layer - 9 Concurrent Implementations
All interfaces and models are ready. Implement ALL services CONCURRENTLY:
[List all 9 services]
Use mocks for any service dependencies to enable true parallel development."

# Verify implementation
READ file "src/services/auth.service.ts"
READ file "src/services/product.service.ts"
RUN "npm test -- --testPathPattern='service.test'"

# Fix any issues
DELEGATE PROMPT="3 service tests are failing. Issues:
1. auth.service: Missing JWT_SECRET in test env
2. product.service: Inventory check not implemented
3. order.service: Payment mock not returning expected format
Fix these specific issues and ensure all service tests pass."
```

### Example 2: API Implementation with Frontend Verification
```
# Understand frontend requirements
READ file "documents/frontend_description.md"
READ file "documents/api_contract.md"

# Implement controllers
DELEGATE PROMPT="Phase: API Controllers
Implement all controllers matching the exact API contract.
Critical: The frontend is already built and expects these exact formats.
Any deviation will break the frontend. Use the documented examples."

# Verify each endpoint
READ file "src/controllers/auth.controller.ts"
RUN "npm test -- src/api-tests/auth.api.test.ts"

# Find mismatch
UPDATE_DOCUMENTATION CONTENT="## API Mismatch Found
Frontend expects: { token, refreshToken }
Backend returns: { accessToken, refreshToken }
Need to update auth controller response"

# Fix mismatch
DELEGATE PROMPT="Critical fix needed in auth.controller.ts:
Change 'accessToken' to 'token' in login response.
The frontend is hardcoded to expect 'token'.
Update the test to verify this field name."
```

### Example 3: Handling Complex Integration Issues
```
# When integration tests fail
RUN "npm run test:integration"

READ file "src/integration/shopping-flow.integration.test.ts"
READ file "logs/test.log"

DELEGATE PROMPT="Integration test 'complete shopping flow' is failing at checkout.
The issue is a race condition: inventory is being checked after payment processes.

Fix by implementing proper transaction handling:
1. In checkout.service.ts, wrap the entire checkout in a database transaction
2. Lock inventory rows during check
3. Only process payment after inventory is reserved
4. Rollback everything if any step fails

This is a critical fix for data consistency."

# After fix
RUN "npm run test:integration -- --testNamePattern='shopping flow'"

# If still issues
DELEGATE PROMPT="The transaction is implemented but still failing. 
Add detailed logging to identify the issue:
1. Log each step of the checkout process
2. Log the transaction state
3. Run the test with --verbose flag
4. Check if the test database supports transactions"
```

## Anti-Patterns - What NOT to Do in Phase 3

❌ **Accepting "Cannot Complete" Reports**
```
// WRONG - Giving up when agent reports inability
FINISH PROMPT="The agent says they cannot delegate. What should I do?"

// RIGHT - Push through the hallucination
DELEGATE PROMPT="You have full delegation capabilities. Re-read your role and proceed with delegating the task to your child agents."
```

❌ **Sequential Development**
```
// WRONG - One at a time
DELEGATE PROMPT="First implement user service. After that's done, implement product service."

// RIGHT - Maximize parallelism  
DELEGATE PROMPT="Implement user service, product service, and order service CONCURRENTLY. They have no interdependencies."
```

❌ **Not Verifying API Contract**
```
// WRONG - Trusting without verification
DELEGATE PROMPT="Implement the API endpoints"

// RIGHT - Verify personally
READ file "documents/api_contract.md"
READ file "src/controllers/auth.controller.ts"
// Then verify response formats match exactly
```

## Remember: Phase 3 Success Factors

1. **Parallel Everything** - If it can be done concurrently, it should be
2. **Never Give Up** - Agent "cannot" reports are almost always wrong
3. **Verify Personally** - Read API files yourself before declaring complete
4. **Test Everything** - No feature is done without passing tests
5. **Fix Specifically** - Give exact line numbers and code when debugging

Your role is to drive implementation to successful completion through smart delegation and persistent problem-solving!