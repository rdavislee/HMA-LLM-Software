# Phase 2: Master Language Examples - Structural Setup and Development Planning

## Core Phase 2 Commands (Focus on RUN for Setup)

### Complete Project Structure Creation
```
# Create main directory structure
RUN "New-Item -ItemType Directory -Path src -Force"
RUN "New-Item -ItemType Directory -Path src/interfaces -Force"
RUN "New-Item -ItemType Directory -Path src/models -Force"
RUN "New-Item -ItemType Directory -Path src/services -Force"
RUN "New-Item -ItemType Directory -Path src/controllers -Force"
RUN "New-Item -ItemType Directory -Path src/middleware -Force"
RUN "New-Item -ItemType Directory -Path src/utils -Force"
RUN "New-Item -ItemType Directory -Path src/config -Force"
RUN "New-Item -ItemType Directory -Path src/database -Force"
RUN "New-Item -ItemType Directory -Path src/database/migrations -Force"
RUN "New-Item -ItemType Directory -Path src/database/seeds -Force"

# Test infrastructure directories
RUN "New-Item -ItemType Directory -Path src/integration -Force"
RUN "New-Item -ItemType Directory -Path src/api-tests -Force"
RUN "New-Item -ItemType Directory -Path src/mocks -Force"
RUN "New-Item -ItemType Directory -Path src/test-helpers -Force"

# Additional structure
RUN "New-Item -ItemType Directory -Path scripts -Force"
RUN "New-Item -ItemType Directory -Path logs -Force"
RUN "New-Item -ItemType Directory -Path .github/workflows -Force"
```

### TypeScript/Node.js Complete Setup
```
# Initialize and configure project
RUN "npm init -y"
RUN "npm pkg set name=\"ecommerce-backend\""
RUN "npm pkg set description=\"Scalable e-commerce backend with TypeScript\""

# Install ALL dependencies at once (child agents cannot install)
RUN "npm install express cors helmet morgan compression body-parser cookie-parser express-rate-limit express-validator"
RUN "npm install jsonwebtoken bcrypt argon2 uuid nanoid"
RUN "npm install pg pg-hstore sequelize sequelize-typescript"
RUN "npm install redis ioredis bull bull-board"
RUN "npm install axios node-fetch got"
RUN "npm install dotenv joi yup class-validator class-transformer"
RUN "npm install lodash date-fns moment dayjs"
RUN "npm install winston winston-daily-rotate-file"
RUN "npm install stripe @sendgrid/mail aws-sdk multer sharp"
RUN "npm install socket.io passport passport-jwt passport-local"

# Development dependencies
RUN "npm install --save-dev typescript @types/node @types/express @types/cors @types/morgan"
RUN "npm install --save-dev @types/jsonwebtoken @types/bcrypt @types/uuid @types/lodash"
RUN "npm install --save-dev ts-node tsx nodemon concurrently"
RUN "npm install --save-dev jest @types/jest ts-jest supertest @types/supertest"
RUN "npm install --save-dev @faker-js/faker jest-extended jest-mock-extended"
RUN "npm install --save-dev eslint prettier @typescript-eslint/parser @typescript-eslint/eslint-plugin"
RUN "npm install --save-dev husky lint-staged commitizen"
RUN "npm install --save-dev webpack webpack-cli webpack-node-externals"
```

### Configuration Files with Proper Settings
```
# TypeScript configuration for strict development
RUN "Set-Content -Path tsconfig.json -Value '{
  \"compilerOptions\": {
    \"target\": \"ES2020\",
    \"module\": \"commonjs\",
    \"lib\": [\"ES2020\"],
    \"outDir\": \"./dist\",
    \"rootDir\": \"./src\",
    \"strict\": true,
    \"esModuleInterop\": true,
    \"skipLibCheck\": true,
    \"forceConsistentCasingInFileNames\": true,
    \"resolveJsonModule\": true,
    \"moduleResolution\": \"node\",
    \"baseUrl\": \".\",
    \"paths\": {
      \"@/*\": [\"src/*\"],
      \"@models/*\": [\"src/models/*\"],
      \"@services/*\": [\"src/services/*\"],
      \"@controllers/*\": [\"src/controllers/*\"],
      \"@utils/*\": [\"src/utils/*\"]
    },
    \"allowJs\": true,
    \"noImplicitAny\": true,
    \"strictNullChecks\": true,
    \"strictFunctionTypes\": true,
    \"noImplicitThis\": true,
    \"noUnusedLocals\": true,
    \"noUnusedParameters\": true,
    \"noImplicitReturns\": true,
    \"noFallthroughCasesInSwitch\": true,
    \"allowSyntheticDefaultImports\": true,
    \"emitDecoratorMetadata\": true,
    \"experimentalDecorators\": true,
    \"sourceMap\": true,
    \"declaration\": true,
    \"declarationMap\": true
  },
  \"include\": [\"src/**/*\"],
  \"exclude\": [\"node_modules\", \"dist\", \"coverage\", \"**/*.test.ts\", \"**/*.spec.ts\"]
}'"

# Jest configuration with proper test setup
RUN "Set-Content -Path jest.config.js -Value 'module.exports = {
  preset: \"ts-jest\",
  testEnvironment: \"node\",
  roots: [\"<rootDir>/src\"],
  testMatch: [
    \"**/__tests__/**/*.ts\",
    \"**/?(*.)+(spec|test).ts\"
  ],
  transform: {
    \"^.+\\.ts$\": \"ts-jest\"
  },
  collectCoverageFrom: [
    \"src/**/*.ts\",
    \"!src/**/*.d.ts\",
    \"!src/**/*.test.ts\",
    \"!src/**/*.spec.ts\",
    \"!src/**/index.ts\",
    \"!src/mocks/**\"
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
    \"^@models/(.*)$\": \"<rootDir>/src/models/$1\",
    \"^@services/(.*)$\": \"<rootDir>/src/services/$1\",
    \"^@controllers/(.*)$\": \"<rootDir>/src/controllers/$1\",
    \"^@utils/(.*)$\": \"<rootDir>/src/utils/$1\"
  },
  setupFilesAfterEnv: [\"<rootDir>/src/test-setup.ts\"],
  testTimeout: 30000,
  verbose: true,
  bail: false,
  errorOnDeprecated\": true
}'"

# Package.json scripts for all operations
RUN "npm pkg set scripts.build=\"tsc --build --verbose\""
RUN "npm pkg set scripts.build:watch=\"tsc --watch\""
RUN "npm pkg set scripts.start=\"node dist/index.js\""
RUN "npm pkg set scripts.dev=\"nodemon\""
RUN "npm pkg set scripts.test=\"jest --detectOpenHandles --forceExit --runInBand\""
RUN "npm pkg set scripts.test:watch=\"jest --watch\""
RUN "npm pkg set scripts.test:coverage=\"jest --coverage\""
RUN "npm pkg set scripts.test:unit=\"jest --testPathPattern='.test.ts$' --runInBand\""
RUN "npm pkg set scripts.test:integration=\"jest --testPathPattern='integration.*test.ts$' --runInBand\""
RUN "npm pkg set scripts.test:api=\"jest --testPathPattern='api-tests.*test.ts$' --runInBand\""
RUN "npm pkg set scripts.test:debug=\"node --inspect-brk ./node_modules/.bin/jest --runInBand\""
RUN "npm pkg set scripts.lint=\"eslint src --ext .ts\""
RUN "npm pkg set scripts.lint:fix=\"eslint src --ext .ts --fix\""
RUN "npm pkg set scripts.format=\"prettier --write 'src/**/*.ts'\""
RUN "npm pkg set scripts.typecheck=\"tsc --noEmit\""
RUN "npm pkg set scripts.validate=\"npm run typecheck && npm run lint && npm run test\""
```

### Creating File Structure with Adjacent Tests
```
# User module with test
RUN "New-Item -ItemType File -Path src/models/user.model.ts"
RUN "New-Item -ItemType File -Path src/models/user.model.test.ts"
RUN "New-Item -ItemType File -Path src/services/user.service.ts"
RUN "New-Item -ItemType File -Path src/services/user.service.test.ts"
RUN "New-Item -ItemType File -Path src/controllers/user.controller.ts"
RUN "New-Item -ItemType File -Path src/controllers/user.controller.test.ts"

# Product module with test
RUN "New-Item -ItemType File -Path src/models/product.model.ts"
RUN "New-Item -ItemType File -Path src/models/product.model.test.ts"
RUN "New-Item -ItemType File -Path src/services/product.service.ts"
RUN "New-Item -ItemType File -Path src/services/product.service.test.ts"
RUN "New-Item -ItemType File -Path src/controllers/product.controller.ts"
RUN "New-Item -ItemType File -Path src/controllers/product.controller.test.ts"

# Integration tests
RUN "New-Item -ItemType File -Path src/integration/user-auth.integration.test.ts"
RUN "New-Item -ItemType File -Path src/integration/product-cart.integration.test.ts"
RUN "New-Item -ItemType File -Path src/integration/order-payment.integration.test.ts"

# API tests matching frontend expectations
RUN "New-Item -ItemType File -Path src/api-tests/auth.api.test.ts"
RUN "New-Item -ItemType File -Path src/api-tests/products.api.test.ts"
RUN "New-Item -ItemType File -Path src/api-tests/cart.api.test.ts"
RUN "New-Item -ItemType File -Path src/api-tests/checkout.api.test.ts"
```

### Setting Up Test Infrastructure
```
# Test setup file
RUN "Set-Content -Path src/test-setup.ts -Value 'import \"jest-extended\";
import { config } from \"dotenv\";

// Load test environment variables
config({ path: \".env.test\" });

// Global test timeout
jest.setTimeout(30000);

// Mock external services
jest.mock(\"@sendgrid/mail\");
jest.mock(\"stripe\");
jest.mock(\"aws-sdk\");

// Suppress console logs during tests
global.console = {
  ...console,
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  info: jest.fn(),
  debug: jest.fn(),
};

// Clean up after each test
afterEach(() => {
  jest.clearAllMocks();
});'"

# Test helpers
RUN "Set-Content -Path src/test-helpers/database.ts -Value 'import { sequelize } from \"@/database/connection\";

export async function cleanDatabase() {
  const tables = Object.keys(sequelize.models);
  await sequelize.query(\"SET FOREIGN_KEY_CHECKS = 0\");
  
  for (const table of tables) {
    await sequelize.query(`TRUNCATE TABLE ${table}`);
  }
  
  await sequelize.query(\"SET FOREIGN_KEY_CHECKS = 1\");
}

export async function seedTestData() {
  // Seed test data implementation
}'"

# API test helper
RUN "Set-Content -Path src/api-tests/helpers/testServer.ts -Value 'import { app } from \"@/app\";
import request from \"supertest\";
import { sequelize } from \"@/database/connection\";

export class TestServer {
  private static instance: TestServer;
  public request: request.SuperTest<request.Test>;

  private constructor() {
    this.request = request(app);
  }

  static getInstance(): TestServer {
    if (!TestServer.instance) {
      TestServer.instance = new TestServer();
    }
    return TestServer.instance;
  }

  async setup() {
    await sequelize.sync({ force: true });
  }

  async teardown() {
    await sequelize.close();
  }
}'"
```

### Development Plan Documentation
```
UPDATE_DOCUMENTATION CONTENT="# Development Plan - Concurrent Implementation Strategy

## Overview
This plan maximizes parallel development through careful module separation and interface-first design.

## Concurrent Development Tracks

### Track 1: Core Models (No Dependencies)
**Team Size**: 3 developers working in parallel
- **Dev 1A**: User & Auth Models
  - src/models/user.model.ts
  - src/models/refresh-token.model.ts
  - All associated tests
  
- **Dev 1B**: Product & Category Models  
  - src/models/product.model.ts
  - src/models/category.model.ts
  - src/models/product-variant.model.ts
  - All associated tests

- **Dev 1C**: Order & Cart Models
  - src/models/cart.model.ts
  - src/models/order.model.ts
  - src/models/order-item.model.ts
  - All associated tests

### Track 2: Service Layer (Depends on Track 1)
**Can start once interfaces are defined**
- **Dev 2A**: Authentication Services
  - src/services/auth.service.ts
  - src/services/token.service.ts
  - src/services/password.service.ts
  
- **Dev 2B**: Product Services
  - src/services/product.service.ts
  - src/services/inventory.service.ts
  - src/services/search.service.ts

- **Dev 2C**: Order Services  
  - src/services/cart.service.ts
  - src/services/order.service.ts
  - src/services/payment.service.ts

### Track 3: API Layer (Depends on Track 2)
**Can use mocks until services complete**
- **Dev 3A**: Auth Controllers
  - src/controllers/auth.controller.ts
  - src/middleware/auth.middleware.ts
  
- **Dev 3B**: Product Controllers
  - src/controllers/product.controller.ts
  - src/controllers/category.controller.ts

- **Dev 3C**: Order Controllers
  - src/controllers/cart.controller.ts
  - src/controllers/order.controller.ts

### Track 4: Integration (Depends on Track 3)
- Integration tests
- API tests matching frontend
- Performance tests
- Security tests

## Dependency Graph
\`\`\`
Interfaces (Day 1)
    |
    ├── Models (Day 1-3)
    |     |
    |     └── Services (Day 2-5)
    |           |
    |           └── Controllers (Day 4-7)
    |                 |
    |                 └── Integration (Day 6-9)
\`\`\`

## Mock Strategy for Parallel Development
1. Create interface definitions first
2. Implement mock services for testing
3. Controllers use mocks until services ready
4. Replace mocks with real implementations
5. Run integration tests to verify

## Risk Mitigation
- Daily sync meetings between tracks
- Shared interface definitions
- Comprehensive mock implementations
- Feature flags for gradual integration
- Automated testing at every level"
```

### Creating Mock Implementations for Parallel Work
```
# Mock auth service
RUN "Set-Content -Path src/mocks/mockAuthService.ts -Value 'import { IAuthService } from \"@/interfaces/IAuthService\";
import { IUser } from \"@/interfaces/IUser\";

export class MockAuthService implements IAuthService {
  private users: Map<string, IUser> = new Map();

  async register(email: string, password: string): Promise<IUser> {
    const user: IUser = {
      id: `mock-${Date.now()}`,
      email,
      passwordHash: \"mock-hash\",
      createdAt: new Date(),
      updatedAt: new Date()
    };
    this.users.set(user.id, user);
    return user;
  }

  async login(email: string, password: string): Promise<{ user: IUser; token: string }> {
    const user = Array.from(this.users.values()).find(u => u.email === email);
    if (!user) throw new Error(\"User not found\");
    
    return {
      user,
      token: \"mock-jwt-token\"
    };
  }

  async validateToken(token: string): Promise<boolean> {
    return token === \"mock-jwt-token\";
  }
}'"

# Mock product service
RUN "Set-Content -Path src/mocks/mockProductService.ts -Value 'import { IProductService } from \"@/interfaces/IProductService\";
import { IProduct } from \"@/interfaces/IProduct\";

export class MockProductService implements IProductService {
  private products: IProduct[] = [
    {
      id: \"1\",
      name: \"Test Product 1\",
      price: 99.99,
      description: \"Test description\",
      inventory: 100,
      category: \"electronics\"
    },
    {
      id: \"2\", 
      name: \"Test Product 2\",
      price: 149.99,
      description: \"Another test\",
      inventory: 50,
      category: \"clothing\"
    }
  ];

  async findAll(filters?: any): Promise<IProduct[]> {
    return this.products;
  }

  async findById(id: string): Promise<IProduct | null> {
    return this.products.find(p => p.id === id) || null;
  }

  async create(data: Partial<IProduct>): Promise<IProduct> {
    const product: IProduct = {
      id: `mock-${Date.now()}`,
      ...data
    } as IProduct;
    this.products.push(product);
    return product;
  }
}'"
```

### Environment Configuration
```
# Development environment
RUN "Set-Content -Path .env.example -Value '# Application
NODE_ENV=development
PORT=3000
API_PREFIX=/api/v1

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecommerce
DB_USER=postgres
DB_PASSWORD=
DB_SSL=false

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# JWT
JWT_SECRET=your-super-secret-key
JWT_EXPIRES_IN=1h
JWT_REFRESH_SECRET=your-refresh-secret
JWT_REFRESH_EXPIRES_IN=7d

# External Services
STRIPE_SECRET_KEY=
SENDGRID_API_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
AWS_S3_BUCKET=

# Frontend
FRONTEND_URL=http://localhost:3001
ALLOWED_ORIGINS=http://localhost:3001,http://localhost:3000'"

# Test environment
RUN "Set-Content -Path .env.test -Value 'NODE_ENV=test
PORT=3001
DB_NAME=ecommerce_test
JWT_SECRET=test-secret
FRONTEND_URL=http://localhost:3001'"
```

### Final Phase 2 Verification
```
# Verify all commands work
RUN "npm run build"
RUN "npm run test"
RUN "npm run lint"

# Create verification script
RUN "Set-Content -Path scripts/verify-setup.js -Value 'console.log(\"Verifying project setup...\");

const fs = require(\"fs\");
const path = require(\"path\");

const requiredDirs = [
  \"src/models\",
  \"src/services\",
  \"src/controllers\",
  \"src/integration\",
  \"src/api-tests\"
];

const requiredFiles = [
  \"tsconfig.json\",
  \"jest.config.js\",
  \".env.example\"
];

let allGood = true;

requiredDirs.forEach(dir => {
  if (!fs.existsSync(dir)) {
    console.error(`Missing directory: ${dir}`);
    allGood = false;
  }
});

requiredFiles.forEach(file => {
  if (!fs.existsSync(file)) {
    console.error(`Missing file: ${file}`);
    allGood = false;
  }
});

if (allGood) {
  console.log(\"✅ All required files and directories present!\");
} else {
  console.error(\"❌ Setup incomplete!\");
  process.exit(1);
}'"

RUN "node scripts/verify-setup.js"

FINISH PROMPT="Phase 2 Complete! 
✅ Created comprehensive directory structure (12 main dirs, 45+ files)
✅ Installed 50+ production and development dependencies
✅ Test infrastructure operational (Jest, Supertest, 80% coverage target)
✅ Configured TypeScript with strict settings
✅ Set up 8 concurrent development tracks
✅ Created mock services for parallel development
✅ All build/test/lint commands verified working

Development plan supports:
- 3 parallel teams on models
- 3 parallel teams on services (with mocks)
- 3 parallel teams on controllers
- Full integration testing suite

Ready to proceed to Phase 3 (Implementation)?"
```

## Phase 2 Anti-Patterns (What NOT to Do)

❌ **NEVER** use DELEGATE in Phase 2:
```
// WRONG - No delegation in Phase 2!
DELEGATE PROMPT="Set up the test infrastructure"
```

❌ **NEVER** create files without tests:
```
// WRONG - Missing test file
RUN "New-Item -ItemType File -Path src/services/user.service.ts"

// RIGHT - Always create test with implementation
RUN "New-Item -ItemType File -Path src/services/user.service.ts"
RUN "New-Item -ItemType File -Path src/services/user.service.test.ts"
```

❌ **NEVER** forget to install dev dependencies:
```
// WRONG - Only production deps
RUN "npm install express jsonwebtoken"

// RIGHT - Include all dev dependencies
RUN "npm install express jsonwebtoken"
RUN "npm install --save-dev @types/express @types/jsonwebtoken jest ts-jest"
```

## Remember: Phase 2 Enables Everything

Your structure and setup in Phase 2 determines:
- How fast development proceeds
- How many developers can work in parallel
- How comprehensive testing will be
- How smooth integration will be

Take time to create the perfect foundation!