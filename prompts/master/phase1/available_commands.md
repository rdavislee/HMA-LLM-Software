# Phase 1: Available Commands - Understanding and Planning

⚠️ **LIMITED TERMINAL ACCESS**: Phase 1 focuses on documentation creation and frontend analysis

## PowerShell Commands for Documentation Setup

### Creating Documentation Structure
```powershell
# Create documents directory if it doesn't exist
RUN "New-Item -ItemType Directory -Path documents -Force"

# Create core documentation files
RUN "New-Item -ItemType File -Path documents/frontend_description.md"
RUN "New-Item -ItemType File -Path documents/api_contract.md"
RUN "New-Item -ItemType File -Path documents/data_models.md"
RUN "New-Item -ItemType File -Path documents/business_logic.md"
RUN "New-Item -ItemType File -Path documents/testing_requirements.md"
RUN "New-Item -ItemType File -Path documents/error_scenarios.md"
RUN "New-Item -ItemType File -Path documents/security_requirements.md"
RUN "New-Item -ItemType File -Path documents/integration_points.md"
RUN "New-Item -ItemType File -Path documents/performance_requirements.md"
```

### Writing Documentation Content
```powershell
# Frontend description
RUN "Set-Content -Path documents/frontend_description.md -Value '# Frontend Description

## Technology Stack
- React 18 with TypeScript
- Material-UI component library
- Redux Toolkit for state management
- Axios for API calls

## Page Structure
1. Landing Page (/)
2. Product Listing (/products)
3. Product Detail (/product/:id)
4. Shopping Cart (/cart)
5. Checkout (/checkout)
6. User Profile (/profile)
7. Order History (/orders)

## API Integration Points
[Document all API calls the frontend makes]'"

# API contract template
RUN "Set-Content -Path documents/api_contract.md -Value '# API Contract Specification

## Base Configuration
- Base URL: /api/v1
- Content-Type: application/json
- Authentication: Bearer token in Authorization header

## Standard Response Formats

### Success Response
{
  \"success\": true,
  \"data\": {},
  \"meta\": {}
}

### Error Response  
{
  \"success\": false,
  \"error\": {
    \"code\": \"ERROR_CODE\",
    \"message\": \"Human readable message\"
  }
}

## Endpoints
[Document each endpoint with request/response examples]'"
```

### Analyzing Frontend Structure
```powershell
# List frontend directory structure
RUN "Get-ChildItem -Path src/frontend -Recurse -Directory | Select-Object FullName"

# Find all API-related files
RUN "Get-ChildItem -Path src/frontend -Recurse -Filter '*api*' -File | Select-Object FullName"
RUN "Get-ChildItem -Path src/frontend -Recurse -Filter '*service*' -File | Select-Object FullName"
RUN "Get-ChildItem -Path src/frontend -Recurse -Filter '*client*' -File | Select-Object FullName"

# Search for API endpoint definitions
RUN "Select-String -Path src/frontend/**/*.js,src/frontend/**/*.ts -Pattern 'fetch|axios|api' -Context 2"

# Find environment variables used
RUN "Select-String -Path src/frontend/**/*.js,src/frontend/**/*.ts -Pattern 'process\.env|REACT_APP_' | Select-Object -Unique"
```

### Creating Data Model Documentation
```powershell
# Create comprehensive data model documentation
RUN "@'
# Data Models

## User Model
\`\`\`typescript
interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: 'admin' | 'customer' | 'vendor';
  createdAt: Date;
  updatedAt: Date;
  emailVerified: boolean;
  profile?: UserProfile;
}
\`\`\`

## Product Model
\`\`\`typescript
interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  currency: string;
  inventory: number;
  category: Category;
  images: Image[];
  variants: ProductVariant[];
  createdAt: Date;
  updatedAt: Date;
}
\`\`\`

## Order Model
\`\`\`typescript
interface Order {
  id: string;
  userId: string;
  items: OrderItem[];
  subtotal: number;
  tax: number;
  shipping: number;
  total: number;
  status: OrderStatus;
  shippingAddress: Address;
  billingAddress: Address;
  createdAt: Date;
  updatedAt: Date;
}
\`\`\`
'@ | Set-Content -Path documents/data_models.md"
```

### Creating Business Rules Documentation
```powershell
RUN "Set-Content -Path documents/business_logic.md -Value '# Business Logic and Rules

## Authentication Rules
1. Users must verify email before making purchases
2. Password must be at least 8 characters with 1 uppercase, 1 number
3. Sessions expire after 24 hours of inactivity
4. Failed login attempts locked after 5 tries

## Order Processing Rules  
1. Inventory must be available at checkout time
2. Prices locked when added to cart
3. Orders cannot be modified after payment
4. Refunds allowed within 30 days

## Product Rules
1. Products must have at least one image
2. Inventory cannot go negative
3. Price changes don't affect existing carts
4. Out-of-stock products remain visible but not purchasable'"
```

### Creating Testing Requirements
```powershell
RUN "@'
# Testing Requirements

## Unit Test Coverage Goals
- Business Logic: 90%
- API Endpoints: 100%  
- Data Models: 80%
- Utilities: 70%

## Integration Test Scenarios
1. Complete user registration flow
2. Full shopping cart workflow
3. Order placement and payment
4. Admin product management
5. Inventory tracking accuracy

## API Test Requirements
Every endpoint must have tests for:
- Success case with valid data
- 400 - Bad request (invalid data)
- 401 - Unauthorized (no/invalid token)
- 403 - Forbidden (wrong role)
- 404 - Not found
- 422 - Validation errors
- 500 - Server errors

## Performance Test Requirements
- API response time < 200ms (95th percentile)
- Support 1000 concurrent users
- Database queries < 50ms
- Page load time < 3 seconds
'@ | Set-Content -Path documents/testing_requirements.md"
```

### Environment Analysis Commands
```powershell
# Check if frontend exists
RUN "Test-Path -Path src/frontend"

# Find package.json to understand dependencies
RUN "Get-Content -Path src/frontend/package.json | ConvertFrom-Json | Select-Object -ExpandProperty dependencies"

# Check for existing API documentation
RUN "Get-ChildItem -Path . -Recurse -Filter '*.md' | Where-Object { $_.Name -match 'api|endpoint|swagger|openapi' }"

# Look for TypeScript interfaces
RUN "Get-ChildItem -Path src/frontend -Recurse -Filter '*.ts' | Where-Object { Select-String -Path $_ -Pattern 'interface|type.*=' -Quiet }"
```

### Creating Security Documentation
```powershell
RUN "Set-Content -Path documents/security_requirements.md -Value '# Security Requirements

## Authentication & Authorization
- JWT tokens with 15-minute expiry
- Refresh tokens with 7-day expiry
- Role-based access control (RBAC)
- Multi-factor authentication for admin accounts

## Data Protection
- All passwords hashed with bcrypt (12 rounds)
- PII encrypted at rest
- HTTPS required for all endpoints
- CORS configured for frontend domain only

## API Security
- Rate limiting: 100 requests/minute per IP
- Request size limit: 10MB
- SQL injection prevention via parameterized queries
- XSS prevention via input sanitization

## Compliance
- GDPR compliant data handling
- PCI DSS for payment processing
- SOC 2 audit logging
- Regular security updates'"
```

### Creating Error Scenario Documentation  
```powershell
RUN "@'
# Error Scenarios and Handling

## Authentication Errors
- Invalid credentials: Return 401 with generic message
- Expired token: Return 401 with \"TOKEN_EXPIRED\" code
- Invalid token: Return 401 with \"INVALID_TOKEN\" code
- Insufficient permissions: Return 403 with role requirements

## Business Logic Errors
- Insufficient inventory: Return 422 with available quantity
- Payment declined: Return 422 with processor message  
- Invalid coupon: Return 422 with expiry info
- Duplicate email: Return 409 with suggestion

## System Errors
- Database connection: Return 503 with retry-after header
- External service down: Return 503 with fallback info
- Server overload: Return 503 with queue position
- Unexpected error: Return 500 with correlation ID

## Client Errors
- Missing required field: Return 400 with field names
- Invalid data format: Return 400 with validation rules
- Resource not found: Return 404 with suggestions
- Method not allowed: Return 405 with allowed methods
'@ | Set-Content -Path documents/error_scenarios.md"
```

### Utility Commands for Phase 1
```powershell
# Create a project overview
RUN "Set-Content -Path documentation.md -Value '# Project Documentation

## Overview
[Comprehensive project description based on human input]

## Key Features
[List all major features identified]

## Technical Stack
[Document all technologies to be used]

## Architecture
[High-level architecture description]'"

# Check what documentation exists
RUN "Get-ChildItem -Path documents -Filter '*.md' | Select-Object Name, Length, LastWriteTime"

# Create a checklist file
RUN "Set-Content -Path documents/phase1_checklist.md -Value '# Phase 1 Completion Checklist

- [ ] Frontend analysis complete
- [ ] All API endpoints documented  
- [ ] Data models defined
- [ ] Business rules documented
- [ ] Error scenarios mapped
- [ ] Security requirements set
- [ ] Performance targets defined
- [ ] Testing strategy outlined
- [ ] Human has approved all documentation'"
```

## Phase 1 Best Practices

1. **Document Everything**: Every decision and requirement must be written down
2. **Use Templates**: Create consistent documentation structure
3. **Version Control Ready**: All docs in markdown for easy tracking
4. **Human Readable**: Write for developers who will implement
5. **Examples Everywhere**: Show don't just tell

Remember: Phase 1 is about understanding and documenting, not implementing. The terminal commands are primarily for creating and organizing documentation files.