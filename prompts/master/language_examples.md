# Master Language Examples

## Core Master Language Directives

### DELEGATE (Single Root Agent)
DELEGATE PROMPT="Phase 1: Implement core data models and interfaces with comprehensive tests"
DELEGATE PROMPT="Build authentication system with login, registration, and session management"
DELEGATE PROMPT="Create REST API endpoints for user management using established interfaces"

### UPDATE_DOCUMENTATION  
UPDATE_DOCUMENTATION CONTENT="# E-commerce Platform\n\n## Product Vision\nA modern e-commerce platform with user authentication, product catalog, shopping cart, and payment processing.\n\n## Core Features\n- User registration and login\n- Product browsing and search\n- Shopping cart management\n- Secure payment processing\n- Order tracking\n\n## Technology Stack\n- Frontend: React with TypeScript\n- Backend: Node.js with Express\n- Database: PostgreSQL\n- Testing: Jest and Mocha"

### READ Operations
READ file "big_picture.md"
READ folder "src"
READ file "requirements.txt", file "package.json"

### RUN Commands (System-Level)
RUN "mkdir -p src/components src/services src/types"
RUN "touch src/types/user.interface.ts"
RUN "npm init -y"
RUN "echo 'node_modules/' > .gitignore"

### SPAWN Tester Agents
SPAWN tester PROMPT="Verify entire project structure and dependencies"
SPAWN tester PROMPT="Test authentication system end-to-end"
SPAWN tester PROMPT="Analyze system performance and identify bottlenecks"

### WAIT for Completion
WAIT

### FINISH for Human Interaction
FINISH PROMPT="I need clarification on the payment system. Should we integrate with Stripe, PayPal, or both?"
FINISH PROMPT="Project structure created! Ready to begin development phases. Does this architecture look correct for your e-commerce platform?"
FINISH PROMPT="Project completed! E-commerce platform with authentication, catalog, cart, and payments. Ready for your review."

## Phase-Based Workflows

### Phase 1: Product Understanding Examples

#### Initial Product Clarification
UPDATE_DOCUMENTATION CONTENT="# Project Requirements (DRAFT)\n\n## User Request\n'Build me a social media app'\n\n## Questions Needed\n- Target audience (teens, professionals, general)?\n- Core features (messaging, posts, video, groups)?\n- Platform (web, mobile, both)?\n- Scale expectations (100s, 1000s, millions of users)?\n- Monetization strategy?\n- Content moderation needs?"

FINISH PROMPT="I need to understand your social media app vision better. What's your target audience - teenagers, professionals, or general users? What core features do you want - messaging, posts, video sharing, groups? Should this be web-based, mobile, or both?"

#### Iterative Understanding Development
UPDATE_DOCUMENTATION CONTENT="# Social Media Platform - Requirements v2\n\n## Confirmed Requirements\n- Target: Young professionals (22-35)\n- Platform: Web-first, mobile-responsive\n- Core Features: Posts, comments, professional networking\n- Scale: 10,000-50,000 initial users\n\n## Technology Decisions\n- Frontend: React with TypeScript\n- Backend: Node.js with Express\n- Database: PostgreSQL for reliability\n- Real-time: WebSocket for live updates\n\n## Still Need Clarification\n- Authentication method (email/password vs OAuth)?\n- Content types (text, images, videos, documents)?\n- Privacy settings complexity?\n- Admin/moderation features needed?"

FINISH PROMPT="Great progress! I understand it's a professional networking platform. Two more clarifications: (1) For authentication, do you prefer simple email/password or social login with Google/LinkedIn? (2) What content types should users be able to post - just text and images, or also videos and documents?"

#### Final Understanding Confirmation
UPDATE_DOCUMENTATION CONTENT="# Professional Networking Platform - Final Requirements\n\n## Product Vision\nA LinkedIn-style professional networking platform for young professionals to connect, share industry insights, and build their careers.\n\n## Core Features\n- User profiles with professional information\n- Post sharing (text, images, documents)\n- Professional connections and networking\n- Company pages and job postings\n- Real-time messaging between connections\n- Content feed with engagement (likes, comments, shares)\n\n## Technical Architecture\n- Frontend: React with TypeScript, responsive design\n- Backend: Node.js with Express.js\n- Database: PostgreSQL with Redis for caching\n- Authentication: JWT with email/password and Google OAuth\n- Real-time: WebSocket for messaging and notifications\n- File Storage: AWS S3 for profile images and documents\n- Deployment: Docker containers on AWS\n\n## Success Metrics\n- User registration and retention\n- Daily active users and engagement\n- Professional connections made\n- Job application conversions"

### Phase 2: Structure Stage Examples

#### Initial Project Structure Creation
RUN "mkdir -p src/components src/services src/types src/utils src/hooks"
RUN "mkdir -p src/pages src/layouts src/contexts"
RUN "mkdir -p test/components test/services test/integration test/e2e"
RUN "mkdir -p public/assets public/images"
RUN "mkdir -p config docs scripts"

#### File Scaffolding
RUN "touch src/types/user.interface.ts"
RUN "touch src/types/post.interface.ts"
RUN "touch src/types/connection.interface.ts"
RUN "touch src/services/auth.service.ts"
RUN "touch src/services/user.service.ts"
RUN "touch src/services/post.service.ts"
RUN "touch src/components/UserProfile.tsx"
RUN "touch src/components/PostFeed.tsx"
RUN "touch src/pages/Login.tsx"
RUN "touch src/pages/Dashboard.tsx"

#### Development Environment Setup
RUN "npm init -y"
RUN "npm install react react-dom typescript @types/react @types/react-dom"
RUN "npm install express jsonwebtoken bcryptjs cors helmet"
RUN "npm install --save-dev jest @types/jest mocha chai supertest"

RUN "echo '{
  \"compilerOptions\": {
    \"target\": \"ES2020\",
    \"module\": \"commonjs\",
    \"lib\": [\"ES2020\", \"DOM\"],
    \"jsx\": \"react-jsx\",
    \"strict\": true,
    \"esModuleInterop\": true,
    \"skipLibCheck\": true
  },
  \"include\": [\"src/**/*\"],
  \"exclude\": [\"node_modules\", \"dist\"]
}' > tsconfig.json"

#### Configuration Files
RUN "echo 'node_modules/
dist/
.env
*.log
.DS_Store' > .gitignore"

RUN "echo '# Professional Networking Platform

## Setup
1. npm install
2. Copy .env.example to .env
3. npm run dev

## Scripts
- npm run dev - Start development server
- npm run build - Build for production  
- npm test - Run test suite
- npm run lint - Run linting

## Architecture
- Frontend: React with TypeScript
- Backend: Node.js with Express
- Database: PostgreSQL
- Authentication: JWT + OAuth
' > README.md"

#### Final Structure Verification
UPDATE_DOCUMENTATION CONTENT="# Project Structure Created\n\n## Directory Architecture\n```\nsrc/\n  ├── components/     # Reusable UI components\n  ├── pages/          # Main application pages\n  ├── services/       # API and business logic\n  ├── types/          # TypeScript interfaces\n  ├── utils/          # Helper functions\n  ├── hooks/          # Custom React hooks\n  ├── contexts/       # React context providers\n  └── layouts/        # Page layout components\n\ntest/\n  ├── components/     # Component tests\n  ├── services/       # Service tests\n  ├── integration/    # Integration tests\n  └── e2e/           # End-to-end tests\n\nconfig/             # Configuration files\ndocs/               # Documentation\npublic/             # Static assets\n```\n\n## Development Environment\n- Package.json configured with React, TypeScript, Express\n- TypeScript configuration for strict type checking\n- Test framework setup with Jest and Mocha\n- Git repository initialized with appropriate .gitignore\n- README with setup instructions\n\n## Ready for Development Phases\nProject structure supports scalable development with clear separation of concerns."

### Phase 3: Project Phases Examples

#### Phase 1: Foundation Development
DELEGATE PROMPT="Phase 1: Core Foundation - Implement all TypeScript interfaces and data models. Create user.interface.ts with User, Profile, and Authentication types. Create post.interface.ts with Post, Comment, and Engagement types. Create connection.interface.ts with Connection and Relationship types. Each interface needs comprehensive JSDoc with preconditions, postconditions, and validation rules. All interfaces must be fully specced before any implementation begins."

WAIT

UPDATE_DOCUMENTATION CONTENT="Phase 1 Complete: All core TypeScript interfaces implemented with comprehensive specifications. Data models ready for implementation phase."

#### Phase 2: Authentication System
DELEGATE PROMPT="Phase 2: Authentication System - Read all interface files from Phase 1. Implement complete authentication system: auth.service.ts for JWT handling, user registration, login, password reset. Create comprehensive test suite in test/services/auth.test.ts covering all success and failure scenarios. Implement User.service.ts for user management operations. All authentication endpoints must be fully tested and secure."

SPAWN tester PROMPT="Verify authentication system security and test coverage"
WAIT

#### Phase 3: User Management
DELEGATE PROMPT="Phase 3: User Management - Read authentication interfaces and services. Implement user profile management: UserProfile.tsx component with edit capabilities, user.service.ts for CRUD operations, profile image upload functionality. Create user management API endpoints. Test all user operations including edge cases and validation failures."

SPAWN tester PROMPT="Test user management system integration with authentication"
WAIT

#### Phase 4: Social Features  
DELEGATE PROMPT="Phase 4: Social Features - Read user and auth implementations. Build core social functionality: PostFeed.tsx component for displaying posts, post.service.ts for post CRUD operations, connection.service.ts for friend/follow relationships, real-time notifications. Implement engagement features (likes, comments, shares). Full test coverage required."

SPAWN tester PROMPT="Test social features and real-time functionality"
WAIT

#### Phase 5: Frontend Integration
DELEGATE PROMPT="Phase 5: Frontend Integration - Read all service implementations. Build complete React frontend: Login.tsx and Dashboard.tsx pages, navigation components, responsive layouts. Integrate all services with React components using custom hooks. Implement state management with React Context. Style with modern CSS/styled-components. Full frontend integration testing."

SPAWN tester PROMPT="End-to-end testing of complete application"
WAIT

#### Final System Verification
SPAWN tester PROMPT="Comprehensive system testing: performance, security, user experience"
SPAWN tester PROMPT="Code quality analysis: test coverage, code maintainability, documentation"
WAIT

UPDATE_DOCUMENTATION CONTENT="# Professional Networking Platform - COMPLETED\n\n## Final Product Summary\nSuccessfully delivered a complete professional networking platform with:\n\n### Implemented Features\n- User authentication and authorization (JWT + OAuth)\n- User profile management with image uploads\n- Post creation and sharing (text, images, documents)\n- Professional connection system\n- Real-time messaging between connections\n- Company pages and job postings\n- Content feed with engagement (likes, comments, shares)\n- Responsive web design\n\n### Technical Implementation\n- Frontend: React with TypeScript, fully responsive\n- Backend: Node.js with Express.js REST API\n- Database: PostgreSQL with optimized queries\n- Authentication: Secure JWT implementation with OAuth integration\n- Real-time: WebSocket for messaging and notifications\n- File Storage: AWS S3 integration for media uploads\n- Testing: 95%+ test coverage across all components\n- Security: Input validation, CORS, helmet, rate limiting\n\n### Quality Assurance\n- All tests passing (unit, integration, e2e)\n- Security audit completed\n- Performance optimized (sub-2s load times)\n- Mobile-responsive design verified\n- Documentation complete\n\n### Deployment Ready\n- Docker containerization complete\n- Environment configuration for staging/production\n- CI/CD pipeline configured\n- Monitoring and logging implemented\n\nProject meets all original requirements and is ready for production deployment."

FINISH PROMPT="Professional networking platform completed! 🎉 Built a LinkedIn-style platform with user auth, profiles, posts, connections, messaging, and company pages. Full React/TypeScript frontend with Node.js backend, 95%+ test coverage, production-ready. The platform supports everything you requested - young professionals can now create profiles, connect, share industry insights, and build their careers. Ready for your final review!"

## Complex Multi-Phase Project Example

### E-commerce Platform Development
```
# Phase 1: Product Understanding
UPDATE_DOCUMENTATION CONTENT="E-commerce platform requirements gathering..."
FINISH PROMPT="Need clarification on payment providers and shipping integration..."

# Phase 2: Structure Creation  
RUN "mkdir -p src/components/cart src/components/product src/components/checkout"
RUN "mkdir -p src/services/payment src/services/inventory src/services/shipping"
RUN "touch src/types/product.interface.ts src/types/order.interface.ts"

# Phase 3: Development Phases
DELEGATE PROMPT="Phase 1: Product catalog with search and filtering"
WAIT
DELEGATE PROMPT="Phase 2: Shopping cart and inventory management" 
WAIT
DELEGATE PROMPT="Phase 3: Checkout and payment processing"
WAIT
DELEGATE PROMPT="Phase 4: Order management and shipping integration"
WAIT

# Final verification
SPAWN tester PROMPT="Full e-commerce platform testing including payment flows"
WAIT
FINISH PROMPT="E-commerce platform complete with catalog, cart, payments, and shipping!"
```

## Human Interaction Patterns

### Clarification Requests
FINISH PROMPT="I need clarification on user roles. Should there be different permission levels (admin, moderator, user), or is this a single-level user system?"

FINISH PROMPT="For the payment system, do you need support for subscriptions and recurring billing, or just one-time purchases?"

FINISH PROMPT="What's your preference for real-time features - should users see live updates when others post, or is periodic refresh acceptable?"

### Progress Updates
FINISH PROMPT="Project structure is ready! I've created a scalable architecture with separate directories for components, services, and types. The setup supports the social media features you described. Should I proceed with development phases?"

FINISH PROMPT="Phase 2 authentication system is complete and fully tested. Users can register, login, reset passwords, and all security measures are in place. Ready to move to user profile management phase?"

### Final Delivery
FINISH PROMPT="Social media platform is complete! 🚀 Users can create profiles, connect with others, share posts with images, message connections in real-time, and discover content through the feed. The platform is responsive, secure, and ready for production. Would you like me to walk you through the key features?"

## Error Handling Examples

### Delegation Issues
READ folder "src"
# If structure is inadequate:
RUN "mkdir -p src/additional/directories" 
UPDATE_DOCUMENTATION CONTENT="Updated project structure to support new requirements..."
DELEGATE PROMPT="Updated task with new architecture..."

### Quality Concerns  
SPAWN tester PROMPT="Investigate performance issues reported in user authentication"
WAIT
# Based on tester feedback:
DELEGATE PROMPT="Optimize authentication system based on performance analysis - implement caching and reduce database queries"

### Scope Changes
UPDATE_DOCUMENTATION CONTENT="UPDATED REQUIREMENTS: Added real-time chat feature to original social media requirements..."
FINISH PROMPT="The scope has expanded to include real-time chat. This affects the architecture significantly. Should I redesign the system to support WebSocket infrastructure, or would you prefer to launch without chat initially?"

## Documentation Evolution Example

### Initial Understanding
UPDATE_DOCUMENTATION CONTENT="# Task Management App\n\n## User Request\n'Build me a todo app'\n\n## Initial Interpretation\nSimple task management application for personal use."

### Expanded Understanding  
UPDATE_DOCUMENTATION CONTENT="# Task Management App - Enhanced\n\n## Product Vision\nTeam-based task management platform with collaboration features\n\n## Core Features\n- Personal and team task lists\n- Task assignment and due dates\n- Progress tracking and reporting\n- Real-time collaboration\n- File attachments and comments\n\n## Technical Requirements\n- Multi-user support with role-based permissions\n- Real-time updates using WebSockets\n- File upload and storage\n- Email notifications\n- Mobile-responsive design"

### Final Specification
UPDATE_DOCUMENTATION CONTENT="# TeamTask Pro - Complete Requirements\n\n## Product Vision\nEnterprise-grade task management platform competing with Asana/Trello\n\n## Feature Set\n- Hierarchical project organization\n- Kanban boards and Gantt charts\n- Team collaboration with comments and mentions\n- Time tracking and reporting\n- Custom fields and automation rules\n- API for third-party integrations\n- Advanced analytics and insights\n\n## Architecture\n- Microservices backend with Node.js\n- React frontend with Redux state management\n- PostgreSQL with Redis caching\n- Docker containerization\n- AWS deployment with auto-scaling\n\n## Success Criteria\n- Support 1000+ concurrent users\n- 99.9% uptime SLA\n- Sub-second response times\n- GDPR compliance\n- Enterprise security standards"

## Key Patterns

1. **Always UPDATE_DOCUMENTATION** before major phase transitions
2. **Use FINISH for human clarification** during product understanding
3. **Structure creation happens in Phase 2** with systematic directory/file creation
4. **Delegation follows dependency order** - interfaces → tests → implementations
5. **SPAWN tester between phases** for quality verification
6. **READ to verify child agent work** before proceeding
7. **Final FINISH celebrates completion** and invites human review 