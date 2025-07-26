# Phase 2: Available Commands - Structural Setup and Development Planning

⚠️ **ELEVATED PRIVILEGES**: Full PowerShell access for comprehensive environment setup

## Directory Structure Creation

### Core Application Structure
```powershell
# Create main source directory
RUN "New-Item -ItemType Directory -Path src -Force"

# Create modular structure for <1000 line files
RUN "New-Item -ItemType Directory -Path src/interfaces -Force"
RUN "New-Item -ItemType Directory -Path src/models -Force"
RUN "New-Item -ItemType Directory -Path src/services -Force"
RUN "New-Item -ItemType Directory -Path src/controllers -Force"
RUN "New-Item -ItemType Directory -Path src/middleware -Force"
RUN "New-Item -ItemType Directory -Path src/routes -Force"
RUN "New-Item -ItemType Directory -Path src/utils -Force"
RUN "New-Item -ItemType Directory -Path src/config -Force"
RUN "New-Item -ItemType Directory -Path src/validators -Force"
RUN "New-Item -ItemType Directory -Path src/decorators -Force"

# Database structure
RUN "New-Item -ItemType Directory -Path src/database -Force"
RUN "New-Item -ItemType Directory -Path src/database/migrations -Force"
RUN "New-Item -ItemType Directory -Path src/database/seeds -Force"
RUN "New-Item -ItemType Directory -Path src/database/entities -Force"

# Test infrastructure (adjacent to implementations)
RUN "New-Item -ItemType Directory -Path src/integration -Force"
RUN "New-Item -ItemType Directory -Path src/api-tests -Force"
RUN "New-Item -ItemType Directory -Path src/performance-tests -Force"
RUN "New-Item -ItemType Directory -Path src/mocks -Force"
RUN "New-Item -ItemType Directory -Path src/test-helpers -Force"
RUN "New-Item -ItemType Directory -Path src/fixtures -Force"

# Additional directories
RUN "New-Item -ItemType Directory -Path scripts -Force"
RUN "New-Item -ItemType Directory -Path logs -Force"
RUN "New-Item -ItemType Directory -Path .docker -Force"
RUN "New-Item -ItemType Directory -Path .github/workflows -Force"
```

## TypeScript/Node.js Project Setup

### Initialize Project
```powershell
# Create package.json
RUN "npm init -y"

# Set package details
RUN "npm pkg set name=\"backend-api\""
RUN "npm pkg set version=\"1.0.0\""
RUN "npm pkg set description=\"Scalable backend API with TypeScript\""
RUN "npm pkg set main=\"dist/index.js\""
RUN "npm pkg set engines.node=\">=16.0.0\""
RUN "npm pkg set engines.npm=\">=8.0.0\""
```

### Install ALL Dependencies (Child Agents Cannot Install)
```powershell
# Core runtime dependencies
RUN "npm install express@4.18.2 cors@2.8.5 helmet@7.0.0 compression@1.7.4"
RUN "npm install body-parser@1.20.2 cookie-parser@1.4.6 express-rate-limit@6.7.0"
RUN "npm install express-validator@7.0.1 morgan@1.10.0 multer@1.4.5-lts.1"

# Authentication & Security
RUN "npm install jsonwebtoken@9.0.0 bcrypt@5.1.0 argon2@0.30.3"
RUN "npm install passport@0.6.0 passport-jwt@4.0.1 passport-local@1.0.0"
RUN "npm install uuid@9.0.0 nanoid@4.0.2 crypto-js@4.1.1"

# Database & ORM
RUN "npm install pg@8.11.0 pg-hstore@2.3.4"
RUN "npm install sequelize@6.32.0 sequelize-typescript@2.1.5"
RUN "npm install typeorm@0.3.16 reflect-metadata@0.1.13"

# Caching & Queues
RUN "npm install redis@4.6.7 ioredis@5.3.2"
RUN "npm install bull@4.10.4 bull-board@2.1.3"
RUN "npm install node-cache@5.1.2"

# External Services
RUN "npm install axios@1.4.0 node-fetch@3.3.1 got@12.6.0"
RUN "npm install stripe@12.9.0 @sendgrid/mail@7.7.0"
RUN "npm install aws-sdk@2.1400.0 @aws-sdk/client-s3@3.360.0"

# Utilities
RUN "npm install dotenv@16.1.4 joi@17.9.2 yup@1.2.0"
RUN "npm install class-validator@0.14.0 class-transformer@0.5.1"
RUN "npm install lodash@4.17.21 date-fns@2.30.0 moment@2.29.4"
RUN "npm install winston@3.9.0 winston-daily-rotate-file@4.7.1"

# Real-time
RUN "npm install socket.io@4.6.2 ws@8.13.0"

# Development dependencies
RUN "npm install --save-dev typescript@5.1.3 @types/node@20.3.1"
RUN "npm install --save-dev @types/express@4.17.17 @types/cors@2.8.13"
RUN "npm install --save-dev @types/jsonwebtoken@9.0.2 @types/bcrypt@5.0.0"
RUN "npm install --save-dev @types/lodash@4.14.195 @types/morgan@1.9.4"
RUN "npm install --save-dev @types/multer@1.4.7 @types/passport@1.0.12"
RUN "npm install --save-dev @types/passport-jwt@3.0.8 @types/uuid@9.0.2"

# Development tools
RUN "npm install --save-dev ts-node@10.9.1 tsx@3.12.7 nodemon@2.0.22"
RUN "npm install --save-dev concurrently@8.2.0 cross-env@7.0.3"

# Testing framework
RUN "npm install --save-dev jest@29.5.0 @types/jest@29.5.2 ts-jest@29.1.0"
RUN "npm install --save-dev supertest@6.3.3 @types/supertest@2.0.12"
RUN "npm install --save-dev @faker-js/faker@8.0.2 jest-extended@4.0.0"
RUN "npm install --save-dev jest-mock-extended@3.0.4"

# Code quality
RUN "npm install --save-dev eslint@8.43.0 prettier@2.8.8"
RUN "npm install --save-dev @typescript-eslint/parser@5.59.11"
RUN "npm install --save-dev @typescript-eslint/eslint-plugin@5.59.11"
RUN "npm install --save-dev eslint-config-prettier@8.8.0"
RUN "npm install --save-dev eslint-plugin-prettier@4.2.1"
RUN "npm install --save-dev husky@8.0.3 lint-staged@13.2.2"

# Build tools
RUN "npm install --save-dev webpack@5.88.0 webpack-cli@5.1.4"
RUN "npm install --save-dev webpack-node-externals@3.0.0"
RUN "npm install --save-dev ts-loader@9.4.3"
```

### Configuration Files

#### TypeScript Configuration
```powershell
RUN "Set-Content -Path tsconfig.json -Value '{
  \"compilerOptions\": {
    \"target\": \"ES2022\",
    \"module\": \"commonjs\",
    \"lib\": [\"ES2022\"],
    \"experimentalDecorators\": true,
    \"emitDecoratorMetadata\": true,
    \"outDir\": \"./dist\",
    \"rootDir\": \"./src\",
    \"strict\": true,
    \"strictNullChecks\": true,
    \"strictFunctionTypes\": true,
    \"strictBindCallApply\": true,
    \"strictPropertyInitialization\": true,
    \"noImplicitThis\": true,
    \"noImplicitAny\": true,
    \"noUnusedLocals\": true,
    \"noUnusedParameters\": true,
    \"noImplicitReturns\": true,
    \"noFallthroughCasesInSwitch\": true,
    \"esModuleInterop\": true,
    \"allowSyntheticDefaultImports\": true,
    \"skipLibCheck\": true,
    \"forceConsistentCasingInFileNames\": true,
    \"resolveJsonModule\": true,
    \"moduleResolution\": \"node\",
    \"baseUrl\": \".\",
    \"paths\": {
      \"@/*\": [\"src/*\"],
      \"@interfaces/*\": [\"src/interfaces/*\"],
      \"@models/*\": [\"src/models/*\"],
      \"@services/*\": [\"src/services/*\"],
      \"@controllers/*\": [\"src/controllers/*\"],
      \"@middleware/*\": [\"src/middleware/*\"],
      \"@utils/*\": [\"src/utils/*\"],
      \"@config/*\": [\"src/config/*\"]
    },
    \"sourceMap\": true,
    \"declaration\": true,
    \"declarationMap\": true,
    \"removeComments\": false,
    \"allowJs\": true,
    \"incremental\": true
  },
  \"include\": [\"src/**/*\"],
  \"exclude\": [\"node_modules\", \"dist\", \"coverage\", \"logs\"]
}'"
```

#### Jest Configuration
```powershell
RUN "Set-Content -Path jest.config.js -Value 'module.exports = {
  preset: \"ts-jest\",
  testEnvironment: \"node\",
  roots: [\"<rootDir>/src\"],
  testMatch: [
    \"**/__tests__/**/*.+(ts|tsx|js)\",
    \"**/?(*.)+(spec|test).+(ts|tsx|js)\"
  ],
  transform: {
    \"^.+\\.(ts|tsx)$\": [\"ts-jest\", {
      tsconfig: {
        jsx: \"react\"
      }
    }]
  },
  collectCoverageFrom: [
    \"src/**/*.{js,jsx,ts,tsx}\",
    \"!src/**/*.d.ts\",
    \"!src/mocks/**\",
    \"!src/test-helpers/**\",
    \"!src/**/*.interface.ts\",
    \"!src/index.ts\"
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  moduleNameMapper: {
    \"^@/(.*)$\": \"<rootDir>/src/$1\",
    \"^@interfaces/(.*)$\": \"<rootDir>/src/interfaces/$1\",
    \"^@models/(.*)$\": \"<rootDir>/src/models/$1\",
    \"^@services/(.*)$\": \"<rootDir>/src/services/$1\",
    \"^@controllers/(.*)$\": \"<rootDir>/src/controllers/$1\",
    \"^@middleware/(.*)$\": \"<rootDir>/src/middleware/$1\",
    \"^@utils/(.*)$\": \"<rootDir>/src/utils/$1\",
    \"^@config/(.*)$\": \"<rootDir>/src/config/$1\"
  },
  setupFilesAfterEnv: [\"<rootDir>/src/test-setup.ts\"],
  testTimeout: 30000,
  verbose: true,
  maxWorkers: \"50%\",
  testPathIgnorePatterns: [\"/node_modules/\", \"/dist/\"],
  watchPathIgnorePatterns: [\"/node_modules/\", \"/dist/\"]
}'"
```

#### Package.json Scripts
```powershell
# Build scripts
RUN "npm pkg set scripts.build=\"tsc --build --verbose\""
RUN "npm pkg set scripts.build:clean=\"tsc --build --clean\""
RUN "npm pkg set scripts.build:watch=\"tsc --build --watch\""

# Development scripts
RUN "npm pkg set scripts.dev=\"nodemon\""
RUN "npm pkg set scripts.start=\"node dist/index.js\""
RUN "npm pkg set scripts.start:prod=\"cross-env NODE_ENV=production node dist/index.js\""

# Test scripts with timeout handling
RUN "npm pkg set scripts.test=\"jest --detectOpenHandles --forceExit --maxWorkers=50%\""
RUN "npm pkg set scripts.test:watch=\"jest --watch\""
RUN "npm pkg set scripts.test:coverage=\"jest --coverage\""
RUN "npm pkg set scripts.test:unit=\"jest --testPathPattern='^(?!.*integration|api).*\\.test\\.ts --maxWorkers=50%\""
RUN "npm pkg set scripts.test:integration=\"jest --testPathPattern='integration.*\\.test\\.ts --runInBand\""
RUN "npm pkg set scripts.test:api=\"jest --testPathPattern='api-tests.*\\.test\\.ts --runInBand\""
RUN "npm pkg set scripts.test:debug=\"node --inspect-brk ./node_modules/.bin/jest --runInBand\""

# Code quality scripts
RUN "npm pkg set scripts.lint=\"eslint . --ext .ts,.js\""
RUN "npm pkg set scripts.lint:fix=\"eslint . --ext .ts,.js --fix\""
RUN "npm pkg set scripts.format=\"prettier --write 'src/**/*.{ts,js,json}'\""
RUN "npm pkg set scripts.typecheck=\"tsc --noEmit\""

# Utility scripts
RUN "npm pkg set scripts.clean=\"rimraf dist coverage logs\""
RUN "npm pkg set scripts.validate=\"npm run typecheck && npm run lint && npm run test\""
RUN "npm pkg set scripts.prepare=\"husky install\""
```

### Create File Structure with Adjacent Tests

```powershell
# User module files
RUN "New-Item -ItemType File -Path src/interfaces/IUser.ts"
RUN "New-Item -ItemType File -Path src/models/user.model.ts"
RUN "New-Item -ItemType File -Path src/models/user.model.test.ts"
RUN "New-Item -ItemType File -Path src/services/user.service.ts"
RUN "New-Item -ItemType File -Path src/services/user.service.test.ts"
RUN "New-Item -ItemType File -Path src/controllers/user.controller.ts"
RUN "New-Item -ItemType File -Path src/controllers/user.controller.test.ts"

# Auth module files
RUN "New-Item -ItemType File -Path src/services/auth.service.ts"
RUN "New-Item -ItemType File -Path src/services/auth.service.test.ts"
RUN "New-Item -ItemType File -Path src/services/token.service.ts"
RUN "New-Item -ItemType File -Path src/services/token.service.test.ts"
RUN "New-Item -ItemType File -Path src/middleware/auth.middleware.ts"
RUN "New-Item -ItemType File -Path src/middleware/auth.middleware.test.ts"

# Product module files
RUN "New-Item -ItemType File -Path src/interfaces/IProduct.ts"
RUN "New-Item -ItemType File -Path src/models/product.model.ts"
RUN "New-Item -ItemType File -Path src/models/product.model.test.ts"
RUN "New-Item -ItemType File -Path src/services/product.service.ts"
RUN "New-Item -ItemType File -Path src/services/product.service.test.ts"
RUN "New-Item -ItemType File -Path src/controllers/product.controller.ts"
RUN "New-Item -ItemType File -Path src/controllers/product.controller.test.ts"

# Integration test files
RUN "New-Item -ItemType File -Path src/integration/auth-user.integration.test.ts"
RUN "New-Item -ItemType File -Path src/integration/product-inventory.integration.test.ts"
RUN "New-Item -ItemType File -Path src/integration/cart-checkout.integration.test.ts"

# API test files
RUN "New-Item -ItemType File -Path src/api-tests/auth.api.test.ts"
RUN "New-Item -ItemType File -Path src/api-tests/products.api.test.ts"
RUN "New-Item -ItemType File -Path src/api-tests/cart.api.test.ts"
RUN "New-Item -ItemType File -Path src/api-tests/orders.api.test.ts"
```

### Environment Configuration

```powershell
# Create environment files
RUN "Set-Content -Path .env.example -Value '# Application
NODE_ENV=development
PORT=3000
API_VERSION=v1
LOG_LEVEL=debug

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
DB_USER=postgres
DB_PASSWORD=password
DB_SSL=false
DB_POOL_MIN=2
DB_POOL_MAX=10

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-this
JWT_EXPIRES_IN=15m
JWT_REFRESH_SECRET=your-super-secret-refresh-key-change-this
JWT_REFRESH_EXPIRES_IN=7d

# Rate Limiting
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX_REQUESTS=100

# External Services
STRIPE_SECRET_KEY=sk_test_
STRIPE_WEBHOOK_SECRET=whsec_
SENDGRID_API_KEY=SG.
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
AWS_S3_BUCKET=myapp-uploads

# Frontend
FRONTEND_URL=http://localhost:3001
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Monitoring
SENTRY_DSN=
DATADOG_API_KEY='"

# Test environment
RUN "Copy-Item -Path .env.example -Destination .env.test"
RUN "Add-Content -Path .env.test -Value \"`nNODE_ENV=test`nDB_NAME=myapp_test`nPORT=3001\""

# Development environment
RUN "Copy-Item -Path .env.example -Destination .env.development"
```

### Create Test Infrastructure

```powershell
# Test setup file
RUN "Set-Content -Path src/test-setup.ts -Value 'import \"jest-extended\";
import { config } from \"dotenv\";
import path from \"path\";

// Load test environment
config({ path: path.resolve(process.cwd(), \".env.test\") });

// Increase test timeout for integration tests
jest.setTimeout(30000);

// Mock external services
jest.mock(\"@sendgrid/mail\");
jest.mock(\"stripe\");
jest.mock(\"aws-sdk\");

// Suppress console during tests
global.console = {
  ...console,
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  info: jest.fn(),
  debug: jest.fn(),
};

// Global test utilities
global.testUtils = {
  async clearDatabase() {
    // Implementation
  },
  async seedDatabase() {
    // Implementation
  }
};

// Cleanup
afterEach(() => {
  jest.clearAllMocks();
});'"

# Test helpers
RUN "Set-Content -Path src/test-helpers/factories.ts -Value 'import { faker } from \"@faker-js/faker\";

export const userFactory = {
  build: (overrides = {}) => ({
    email: faker.internet.email(),
    password: \"Test123!@#\",
    firstName: faker.person.firstName(),
    lastName: faker.person.lastName(),
    ...overrides
  })
};

export const productFactory = {
  build: (overrides = {}) => ({
    name: faker.commerce.productName(),
    description: faker.commerce.productDescription(),
    price: parseFloat(faker.commerce.price()),
    inventory: faker.number.int({ min: 0, max: 1000 }),
    category: faker.commerce.department(),
    ...overrides
  })
};'"
```

### Create Mock Services for Parallel Development

```powershell
# Mock auth service
RUN "Set-Content -Path src/mocks/mockAuthService.ts -Value 'export class MockAuthService {
  async login(email: string, password: string) {
    if (email === \"test@example.com\" && password === \"password\") {
      return {
        token: \"mock-jwt-token\",
        refreshToken: \"mock-refresh-token\",
        user: { id: \"123\", email }
      };
    }
    throw new Error(\"Invalid credentials\");
  }

  async validateToken(token: string) {
    return token === \"mock-jwt-token\";
  }

  async refreshToken(refreshToken: string) {
    if (refreshToken === \"mock-refresh-token\") {
      return { token: \"new-mock-jwt-token\" };
    }
    throw new Error(\"Invalid refresh token\");
  }
}'"
```

### Additional Configuration Files

```powershell
# Nodemon configuration
RUN "Set-Content -Path nodemon.json -Value '{
  \"watch\": [\"src\"],
  \"ext\": \"ts,json\",
  \"ignore\": [\"src/**/*.test.ts\", \"src/**/*.spec.ts\"],
  \"exec\": \"ts-node -r tsconfig-paths/register src/index.ts\",
  \"env\": {
    \"NODE_ENV\": \"development\"
  }
}'"

# ESLint configuration
RUN "Set-Content -Path .eslintrc.json -Value '{
  \"parser\": \"@typescript-eslint/parser\",
  \"extends\": [
    \"eslint:recommended\",
    \"plugin:@typescript-eslint/recommended\",
    \"prettier\"
  ],
  \"plugins\": [\"@typescript-eslint\", \"prettier\"],
  \"env\": {
    \"node\": true,
    \"es2022\": true,
    \"jest\": true
  },
  \"rules\": {
    \"@typescript-eslint/no-explicit-any\": \"warn\",
    \"@typescript-eslint/no-unused-vars\": \"error\",
    \"prettier/prettier\": \"error\"
  }
}'"

# Prettier configuration
RUN "Set-Content -Path .prettierrc -Value '{
  \"semi\": true,
  \"trailingComma\": \"all\",
  \"singleQuote\": true,
  \"printWidth\": 100,
  \"tabWidth\": 2,
  \"useTabs\": false
}'"

# Git ignore
RUN "Set-Content -Path .gitignore -Value 'node_modules/
dist/
coverage/
logs/
*.log
.env
.env.local
.env.*.local
.DS_Store
*.tmp
*.temp
.vscode/
.idea/
*.swp
*.swo'"
```

### Verify Setup

```powershell
# Test TypeScript compilation
RUN "npx tsc --noEmit"

# Run placeholder tests
RUN "npm test -- --passWithNoTests"

# Check file structure
RUN "Get-ChildItem -Path src -Recurse -Directory | Select-Object FullName"

# Verify all dependencies installed
RUN "npm list --depth=0"
```

### Create Development Plan

```powershell
RUN "Set-Content -Path documents/development_plan.md -Value '# Development Plan

## Concurrent Development Tracks

### Track 1: Core Infrastructure (Day 1-2)
**3 Developers**
- Dev 1A: Database models and migrations
- Dev 1B: Redis setup and caching layer
- Dev 1C: Logger, error handler, base classes

### Track 2: Business Entities (Day 2-4)
**4 Developers - Can start after interfaces defined**
- Dev 2A: User and auth services
- Dev 2B: Product and inventory services
- Dev 2C: Cart and order services
- Dev 2D: Payment and notification services

### Track 3: API Layer (Day 3-5)
**3 Developers - Can use mocks initially**
- Dev 3A: Auth and user controllers
- Dev 3B: Product and search controllers
- Dev 3C: Order and payment controllers

### Track 4: Testing (Day 4-6)
**2 Developers**
- Dev 4A: Integration tests
- Dev 4B: API tests and performance tests

## Dependency Management
- All teams can work with interfaces defined
- Mock services enable parallel controller development
- Integration happens incrementally, not all at once

## Risk Mitigation
- Daily sync meetings at module boundaries
- Continuous integration runs all tests
- Feature flags for gradual rollout
- Monitoring from day one'"
```

## Best Practices for Phase 2

1. **Install Everything**: Child agents cannot install packages
2. **Create All Test Files**: Every implementation needs adjacent test
3. **Enable Parallelism**: Structure allows concurrent development
4. **Configure Properly**: All tools configured and working
5. **Mock Dependencies**: Enable truly parallel development

Remember: The structure and setup you create here determines the entire project's development speed and quality.