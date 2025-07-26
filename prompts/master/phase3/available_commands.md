# Phase 3: Available Commands - Implementation

✅ **FULL COMMAND ACCESS**: All terminal commands for testing, debugging, and verification

## Testing Commands

### Running Test Suites
```powershell
# Run all tests
RUN "npm test"

# Run specific test categories
RUN "npm run test:unit"
RUN "npm run test:integration"
RUN "npm run test:api"

# Run tests with coverage
RUN "npm run test:coverage"

# Run tests in watch mode
RUN "npm run test:watch"

# Run specific test file
RUN "npm test -- src/services/auth.service.test.ts"
RUN "npm test -- src/api-tests/products.api.test.ts --verbose"

# Run tests matching pattern
RUN "npm test -- --testNamePattern='should login with valid credentials'"
RUN "npm test -- --testPathPattern='auth' --verbose"

# Debug a specific test
RUN "node --inspect-brk ./node_modules/.bin/jest --runInBand src/services/user.service.test.ts"
```

### Test Timeout Solutions
```powershell
# For long-running tests, use proper timeouts in test files, NOT NO_TIMEOUT
# Run tests with custom timeout
RUN "npm test -- --testTimeout=60000"

# Run tests sequentially to avoid timeouts
RUN "npm test -- --runInBand"

# Run tests with fewer workers
RUN "npm test -- --maxWorkers=2"

# Split test runs by type
RUN "npm test -- --testPathPattern='unit'"
RUN "npm test -- --testPathPattern='integration'"
RUN "npm test -- --testPathPattern='api'"
```

## Debugging Commands

### Analyzing Test Failures
```powershell
# Get detailed error output
RUN "npm test -- --verbose --no-coverage"

# Run single test with full stack trace
RUN "npm test -- --detectOpenHandles --verbose src/services/auth.service.test.ts"

# Check for open handles preventing Jest from exiting
RUN "npm test -- --detectOpenHandles"

# Find which test is hanging
RUN "npm test -- --verbose --runInBand"
```

### TypeScript Compilation Debugging
```powershell
# Check for TypeScript errors
RUN "npx tsc --noEmit"

# Show detailed compilation errors
RUN "npx tsc --noEmit --pretty --skipLibCheck false"

# Check specific file
RUN "npx tsc --noEmit src/controllers/auth.controller.ts"

# List all files that would be compiled
RUN "npx tsc --listFiles"

# Show resolved module paths
RUN "npx tsc --traceResolution | grep 'auth.service'"
```

### Dependency Analysis
```powershell
# Check for missing dependencies
RUN "npm ls"

# Find duplicate dependencies
RUN "npm ls --depth=0"

# Check why a package is installed
RUN "npm explain express"

# Audit dependencies for vulnerabilities
RUN "npm audit"

# Check outdated packages
RUN "npm outdated"
```

## Build and Verification Commands

### Building the Project
```powershell
# Clean build
RUN "npm run build:clean && npm run build"

# Build with source maps
RUN "npx tsc --sourceMap"

# Watch mode for development
RUN "npm run build:watch"

# Build specific module
RUN "npx tsc src/services/auth.service.ts --outDir dist"
```

### Running the Application
```powershell
# Start in development mode
RUN "npm run dev"

# Start production build
RUN "npm start"

# Start with specific environment
RUN "cross-env NODE_ENV=production npm start"

# Start with debugging
RUN "node --inspect dist/index.js"

# Start with specific port
RUN "cross-env PORT=4000 npm start"
```

## Code Quality Commands

### Linting and Formatting
```powershell
# Run ESLint
RUN "npm run lint"

# Fix linting issues
RUN "npm run lint:fix"

# Lint specific directory
RUN "npx eslint src/controllers --ext .ts"

# Format code
RUN "npm run format"

# Check formatting without changing
RUN "npx prettier --check 'src/**/*.ts'"
```

### Type Checking
```powershell
# Full type check
RUN "npm run typecheck"

# Type check with specific config
RUN "npx tsc --noEmit --strict"

# Check for unused exports
RUN "npx ts-prune"
```

## API Testing Commands

### Testing API Endpoints
```powershell
# Run all API tests
RUN "npm run test:api"

# Test specific endpoint
RUN "npm test -- src/api-tests/auth.api.test.ts --verbose"

# Run API tests with real database
RUN "cross-env NODE_ENV=test npm run test:api"

# Test with specific timeout for slow endpoints
RUN "npm test -- src/api-tests/checkout.api.test.ts --testTimeout=30000"
```

### Manual API Testing
```powershell
# Start server and test with curl
RUN "npm run dev"

# In another terminal:
RUN "curl -X POST http://localhost:3000/api/auth/login -H 'Content-Type: application/json' -d '{\"email\":\"test@example.com\",\"password\":\"password\"}'"

# Test with verbose output
RUN "curl -v -X GET http://localhost:3000/api/products"

# Test with authentication header
RUN "curl -X GET http://localhost:3000/api/users/profile -H 'Authorization: Bearer YOUR_TOKEN_HERE'"
```

## Database Commands

### Database Management
```powershell
# Run migrations
RUN "npx sequelize-cli db:migrate"

# Rollback migration
RUN "npx sequelize-cli db:migrate:undo"

# Create seed data
RUN "npx sequelize-cli db:seed:all"

# Reset database
RUN "npx sequelize-cli db:drop && npx sequelize-cli db:create && npx sequelize-cli db:migrate"
```

### Database Debugging
```powershell
# Check database connection
RUN "node -e \"require('./dist/config/database').sequelize.authenticate().then(() => console.log('Connected')).catch(err => console.error(err))\""

# List all tables
RUN "node -e \"require('./dist/config/database').sequelize.query('SELECT tablename FROM pg_tables WHERE schemaname = \\'public\\';').then(([results]) => console.log(results))\""
```

## Performance Testing

### Load Testing
```powershell
# Simple load test with autocannon
RUN "npx autocannon -c 100 -d 30 http://localhost:3000/api/products"

# Test specific endpoint with body
RUN "npx autocannon -c 50 -d 20 -m POST -H 'Content-Type: application/json' -b '{\"email\":\"test@example.com\",\"password\":\"password\"}' http://localhost:3000/api/auth/login"
```

### Memory Analysis
```powershell
# Run with memory profiling
RUN "node --expose-gc --inspect dist/index.js"

# Check memory usage
RUN "node -e \"console.log(process.memoryUsage())\""
```

## Debugging Specific Issues

### JWT/Authentication Issues
```powershell
# Test JWT secret is loaded
RUN "node -e \"console.log('JWT_SECRET:', process.env.JWT_SECRET ? 'Loaded' : 'Missing')\""

# Decode a JWT token
RUN "node -e \"const jwt = require('jsonwebtoken'); console.log(jwt.decode('YOUR_TOKEN_HERE'))\""

# Verify token manually
RUN "node -e \"const jwt = require('jsonwebtoken'); jwt.verify('YOUR_TOKEN_HERE', process.env.JWT_SECRET, (err, decoded) => console.log(err || decoded))\""
```

### Module Resolution Issues
```powershell
# Check module can be imported
RUN "node -e \"try { require('./dist/services/auth.service'); console.log('Module loaded successfully'); } catch(e) { console.error(e); }\""

# Find where module is located
RUN "node -e \"console.log(require.resolve('./dist/services/auth.service'))\""

# List all compiled files
RUN "Get-ChildItem -Path dist -Recurse -Filter '*.js' | Select-Object FullName"
```

### Environment Variable Issues
```powershell
# Check all environment variables
RUN "node -e \"console.log(process.env)\""

# Check specific variables
RUN "node -e \"console.log({NODE_ENV: process.env.NODE_ENV, PORT: process.env.PORT, DB_HOST: process.env.DB_HOST})\""

# Load env file and check
RUN "node -r dotenv/config -e \"console.log('DB_NAME:', process.env.DB_NAME)\""
```

## Integration Testing Commands

### Running Integration Tests
```powershell
# Run all integration tests
RUN "npm run test:integration"

# Run with real database
RUN "cross-env NODE_ENV=test npm run test:integration"

# Run specific integration test
RUN "npm test -- src/integration/auth-user.integration.test.ts --runInBand"

# Debug integration test
RUN "node --inspect-brk ./node_modules/.bin/jest --runInBand src/integration/shopping-flow.integration.test.ts"
```

## Verification Commands

### Final Verification Before Completion
```powershell
# Full validation
RUN "npm run validate"

# Build and test
RUN "npm run build && npm test"

# Check all endpoints are working
RUN "npm run test:api -- --verbose"

# Verify test coverage meets requirements
RUN "npm run test:coverage -- --coverageReporters=text"

# Security audit
RUN "npm audit --production"

# Check for TypeScript errors
RUN "npm run typecheck"

# Lint check
RUN "npm run lint"
```

### Creating Test Reports
```powershell
# Generate HTML coverage report
RUN "npm run test:coverage -- --coverageReporters=html"

# Generate test results in JSON
RUN "npm test -- --json --outputFile=test-results.json"

# Generate JUnit format for CI
RUN "npm test -- --reporters=jest-junit"
```

## Quick Debugging Checklist

```powershell
# When tests fail mysteriously
RUN "npm test -- --clearCache"
RUN "Remove-Item -Path node_modules -Recurse -Force"
RUN "npm install"
RUN "npm run build:clean && npm run build"
RUN "npm test"

# When "Cannot find module" errors occur
RUN "npm run build"
RUN "npx tsc --traceResolution | Select-String 'yourModule'"

# When database tests fail
RUN "cross-env NODE_ENV=test node -e \"require('./dist/config/database').testConnection()\""
```

## Remember

- Never use NO_TIMEOUT for tests - split them instead
- Always run tests before declaring features complete
- Use --runInBand for debugging race conditions
- Check environment variables when authentication fails
- Clear Jest cache when tests behave strangely