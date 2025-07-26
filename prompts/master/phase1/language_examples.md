# Phase 1: Master Language Examples - Understanding and Planning

## Core Phase 1 Commands (NO DELEGATION AVAILABLE)

### READ Operations - Frontend Analysis
```
READ file "src/frontend/App.tsx"
READ file "src/frontend/api/authService.ts", file "src/frontend/api/productService.ts"
READ folder "src/frontend/hooks", folder "src/frontend/components"
READ file "src/frontend/utils/apiClient.ts"
```

### UPDATE_DOCUMENTATION - Building Specifications
```
UPDATE_DOCUMENTATION CONTENT="# E-Commerce Platform Specification\n\n## 1. Executive Summary\nA full-stack e-commerce platform enabling B2C transactions with real-time inventory, secure payments, and administrative controls.\n\n## 2. System Architecture\n\n### 2.1 Frontend (Provided)\n- React 18 with TypeScript\n- Material-UI components\n- Redux Toolkit for state management\n- Axios for API communication\n\n### 2.2 Backend (To Be Built)\n- Node.js with Express\n- PostgreSQL database\n- Redis for caching\n- JWT authentication\n\n## 3. Functional Requirements\n\n### 3.1 User Management\n#### 3.1.1 Registration\n- Email/password registration\n- Email verification required\n- Profile completion wizard\n- GDPR-compliant data handling\n\n#### 3.1.2 Authentication\n- JWT-based authentication\n- Refresh token mechanism\n- Session timeout: 24 hours\n- Remember me: 30 days\n\n### 3.2 Product Catalog\n#### 3.2.1 Product Model\n```typescript\ninterface Product {\n  id: string;\n  name: string;\n  description: string;\n  price: number;\n  currency: 'USD' | 'EUR' | 'GBP';\n  inventory: number;\n  category: Category;\n  images: Image[];\n  variants: ProductVariant[];\n  metadata: Record<string, any>;\n}\n```\n\n## 4. API Specification\n\n### 4.1 Authentication Endpoints\n\n#### POST /api/auth/register\n**Purpose**: Create new user account\n**Request**:\n```json\n{\n  \"email\": \"user@example.com\",\n  \"password\": \"SecurePass123!\",\n  \"firstName\": \"John\",\n  \"lastName\": \"Doe\",\n  \"acceptTerms\": true\n}\n```\n**Response (201)**:\n```json\n{\n  \"success\": true,\n  \"message\": \"Registration successful. Please check your email to verify your account.\",\n  \"userId\": \"550e8400-e29b-41d4-a716-446655440000\"\n}\n```\n**Error Response (400)**:\n```json\n{\n  \"success\": false,\n  \"error\": \"EMAIL_ALREADY_EXISTS\",\n  \"message\": \"An account with this email already exists.\"\n}\n```"
```

### RUN Commands - Creating Documentation Structure
```
RUN "New-Item -ItemType Directory -Path documents -Force"
RUN "New-Item -ItemType File -Path documents/frontend_description.md"
RUN "Set-Content -Path documents/frontend_description.md -Value '# Frontend Description\n\n## Overview\nThe frontend is a modern React application built with TypeScript and Material-UI.\n\n## Key Features\n1. Responsive design (mobile-first)\n2. Progressive Web App capabilities\n3. Offline cart functionality\n4. Real-time inventory updates via WebSocket\n\n## Page Structure\n\n### 1. Landing Page (/)\n- Hero banner with promotions\n- Featured products carousel\n- Category grid\n- Newsletter signup\n\n### 2. Product Listing (/products)\n- Filter sidebar (price, category, brand, rating)\n- Sort options (price, popularity, newest)\n- Pagination (20 items per page)\n- Quick view modal\n\n### 3. Product Detail (/product/:id)\n- Image gallery with zoom\n- Variant selector (size, color)\n- Stock availability indicator\n- Add to cart with quantity\n- Reviews section\n- Related products\n\n### 4. Shopping Cart (/cart)\n- Line items with images\n- Quantity adjustment\n- Remove items\n- Price breakdown\n- Promo code input\n- Checkout button\n\n## API Integration Points\n\nThe frontend expects these API endpoints:\n\n### Authentication\n- POST /api/auth/login\n- POST /api/auth/logout\n- POST /api/auth/refresh\n- GET /api/auth/me\n\n### Products\n- GET /api/products (with query params for filtering)\n- GET /api/products/:id\n- GET /api/products/:id/reviews\n- POST /api/products/:id/reviews\n\n### Cart\n- GET /api/cart\n- POST /api/cart/items\n- PUT /api/cart/items/:itemId\n- DELETE /api/cart/items/:itemId\n- POST /api/cart/checkout'"
```

### FINISH Commands - Requirements Gathering
```
FINISH PROMPT="I've analyzed the frontend structure. The authentication flow appears to use JWT tokens stored in localStorage. I need to understand:\n\n1. Security Requirements:\n   - Should we implement refresh tokens?\n   - Is two-factor authentication required?\n   - Any specific password complexity rules?\n   \n2. Session Management:\n   - How long should sessions last?\n   - Should we support concurrent sessions?\n   - Auto-logout on inactivity?\n\nPlease provide your requirements for authentication security."

FINISH PROMPT="Regarding the product catalog, I found the frontend expects:\n- Product filtering by multiple categories\n- Price range filters\n- Brand filters\n- Color/size variants\n\nQuestions:\n1. How should out-of-stock products be handled?\n2. Should prices vary by user location/currency?\n3. Are there bulk discount rules?\n4. Do products have limited-time offers?\n5. Should we track view/purchase statistics?"

FINISH PROMPT="For the shopping cart functionality, I need clarification on:\n\n1. Cart Persistence:\n   - Guest carts - how long to preserve?\n   - Merge guest cart on login?\n   - Cart abandonment emails?\n\n2. Inventory Handling:\n   - Reserve items when added to cart?\n   - How long to hold reservations?\n   - What if items go out of stock while in cart?\n\n3. Pricing:\n   - When to calculate taxes?\n   - Shipping calculation method?\n   - Support for discount codes?\n   - Multiple currency support?"
```

## Phase 1 Workflow Examples

### Example 1: Initial Project Understanding
```
UPDATE_DOCUMENTATION CONTENT="# Project Understanding - DRAFT\n\n## Initial Request\nBuild backend for e-commerce platform\n\n## Questions to Clarify\n1. What products are being sold?\n2. B2B or B2C?\n3. Geographic scope?\n4. Payment methods?\n5. Shipping requirements?"

FINISH PROMPT="I need to understand the core business model. Could you tell me:\n1. What types of products will be sold (physical/digital)?\n2. Target market (B2B/B2C)?\n3. Expected transaction volume?\n4. Geographic scope (single country/international)?\n5. Any specific industry regulations?"

// After human response...

UPDATE_DOCUMENTATION CONTENT="# Project Understanding - v2\n\n## Business Model\n- B2C physical products\n- Fashion and accessories\n- US market initially\n- 1000-5000 transactions/day expected\n- Standard e-commerce regulations apply\n\n## Next Questions\n- Payment processor preference?\n- Shipping integration needs?\n- Return/refund policies?"
```

### Example 2: Frontend Integration Analysis
```
READ file "src/frontend/services/apiClient.ts"
READ file "src/frontend/types/api.types.ts"
READ folder "src/frontend/features/auth"

UPDATE_DOCUMENTATION CONTENT="## Frontend API Analysis\n\n### Discovered Endpoints\n\nFrom apiClient.ts:\n```typescript\n// Authentication\npost('/api/auth/login', credentials)\npost('/api/auth/logout')\nget('/api/auth/user')\npost('/api/auth/forgot-password', { email })\npost('/api/auth/reset-password', { token, password })\n\n// Products\nget('/api/products', { params: filters })\nget('/api/products/:id')\nget('/api/products/categories')\nget('/api/products/:id/related')\n\n// Cart\nget('/api/cart')\npost('/api/cart/add', { productId, quantity, variant })\nput('/api/cart/update/:itemId', { quantity })\ndelete('/api/cart/remove/:itemId')\npost('/api/cart/apply-coupon', { code })\n```"

FINISH PROMPT="I've discovered the frontend expects 16 API endpoints. The authentication flow uses JWT tokens with a refresh mechanism. Should the backend implement rate limiting on these endpoints? Also, what should happen if a user tries to add more items to cart than available inventory?"
```

### Example 3: Creating Comprehensive Documentation
```
RUN "New-Item -ItemType File -Path documents/api_contract.md"
RUN "Set-Content -Path documents/api_contract.md -Value '# API Contract Specification\n\n## Overview\nThis document defines the complete API contract between frontend and backend.\n\n## Base Configuration\n- Base URL: https://api.example.com/v1\n- Content-Type: application/json\n- Authentication: Bearer token in Authorization header\n\n## Standard Response Format\n\n### Success Response\n```json\n{\n  \"success\": true,\n  \"data\": { },\n  \"meta\": {\n    \"timestamp\": \"2024-01-15T10:30:00Z\",\n    \"version\": \"1.0\"\n  }\n}\n```\n\n### Error Response\n```json\n{\n  \"success\": false,\n  \"error\": {\n    \"code\": \"VALIDATION_ERROR\",\n    \"message\": \"Invalid input data\",\n    \"details\": []\n  }\n}\n```'"

RUN "New-Item -ItemType File -Path documents/testing_requirements.md"
RUN "Set-Content -Path documents/testing_requirements.md -Value '# Testing Requirements\n\n## Unit Test Coverage\n- Minimum 80% code coverage\n- All business logic must have tests\n- All API endpoints must have tests\n\n## Integration Tests\n- Database operations\n- External service integrations\n- Authentication flow\n- Payment processing\n\n## API Test Scenarios\n\n### Authentication Tests\n1. Successful login with valid credentials\n2. Failed login with invalid credentials\n3. Token refresh flow\n4. Logout invalidates token\n5. Protected route access without token\n6. Expired token handling\n\n### Product Tests\n1. List products with pagination\n2. Filter products by category\n3. Search products by name\n4. Get single product details\n5. Handle non-existent product\n\n### Cart Tests\n1. Add item to cart\n2. Update item quantity\n3. Remove item from cart\n4. Apply valid coupon\n5. Apply invalid coupon\n6. Cart total calculation\n7. Empty cart handling'"
```

### Example 4: Final Phase 1 Summary
```
UPDATE_DOCUMENTATION CONTENT="# E-Commerce Platform - Final Specification\n\n## Project Summary\nA modern B2C e-commerce platform for fashion and accessories with the following core features:\n- User authentication with JWT\n- Product catalog with advanced filtering\n- Shopping cart with real-time inventory\n- Secure payment processing\n- Order management\n- Admin dashboard\n\n## Architecture Decisions\n- Backend: Node.js with Express\n- Database: PostgreSQL with Redis cache\n- Authentication: JWT with refresh tokens\n- Payment: Stripe integration\n- File Storage: AWS S3\n- Email: SendGrid\n- Monitoring: DataDog\n\n## Documented Specifications\n1. ✅ API Contract (documents/api_contract.md)\n2. ✅ Data Models (documents/data_models.md)\n3. ✅ Frontend Description (documents/frontend_description.md)\n4. ✅ Business Logic (documents/business_logic.md)\n5. ✅ Testing Requirements (documents/testing_requirements.md)\n6. ✅ Error Scenarios (documents/error_scenarios.md)\n7. ✅ Security Requirements (documents/security_requirements.md)\n\n## Success Criteria\n- All API endpoints return correct data formats\n- Authentication is secure and follows OWASP guidelines\n- Cart operations handle race conditions\n- Payment processing is PCI compliant\n- 95% uptime with <200ms response times\n- Comprehensive test coverage (>80%)"

FINISH PROMPT="I have completed the comprehensive documentation for the e-commerce platform. All API endpoints are specified with examples, error cases are documented, and testing requirements are defined. The frontend integration points are fully understood. Ready to proceed to Phase 2 (Structure Setup)?"
```

## Phase 1 Anti-Patterns (What NOT to Do)

❌ **NEVER** use DELEGATE in Phase 1:
```
// WRONG - No delegation in Phase 1!
DELEGATE PROMPT="Create the initial structure"
```

❌ **NEVER** assume requirements:
```
// WRONG - Always ask first!
UPDATE_DOCUMENTATION CONTENT="Using standard JWT authentication with 1-hour expiry"

// RIGHT - Clarify first
FINISH PROMPT="What should the JWT token expiry time be? Industry standard is 15-60 minutes for access tokens."
```

❌ **NEVER** skip frontend analysis:
```
// WRONG - Ignoring frontend
UPDATE_DOCUMENTATION CONTENT="Backend will have standard REST endpoints"

// RIGHT - Analyze frontend first
READ folder "src/frontend/api"
FINISH PROMPT="The frontend expects these 12 endpoints: [list]. Are there additional endpoints needed?"
```

## Remember: Phase 1 Sets Project Success

Your documentation in Phase 1 is the foundation everything builds upon. Take time to:
- Understand every requirement
- Document every API endpoint
- Clarify every ambiguity
- Plan for every edge case

The better your Phase 1 documentation, the smoother Phases 2 and 3 will be!