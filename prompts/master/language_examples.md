Master Language Examples
Core Master Language Directives
DELEGATE (Single Root Agent)
DELEGATE PROMPT="Phase 1: Implement core data models and interfaces with comprehensive tests using OOP principles"
DELEGATE PROMPT="Build authentication system with login, registration, session management using proper encapsulation"
DELEGATE PROMPT="Create REST API endpoints using established interfaces with clean abstraction layers"
UPDATE_DOCUMENTATION
UPDATE_DOCUMENTATION CONTENT="# E-commerce Platform\n\n## Product Vision\nModern e-commerce with auth, catalog, cart, payments\n\n## Core Features\n- User registration/login\n- Product catalog/search\n- Shopping cart\n- Payment processing\n- Order tracking\n\n## Tech Stack\n- Frontend: React/TypeScript\n- Backend: Node.js/Express\n- Database: PostgreSQL\n- Testing: Jest/Mocha"
READ Operations
READ file "documentation.md"
READ folder "src"
READ file "requirements.txt", file "package.json"
READ folder "src/components", folder "src/services"
RUN Commands (PowerShell)
RUN "New-Item -ItemType Directory -Path src/components -Force"
RUN "New-Item -ItemType File -Path src/types/user.interface.ts"
RUN "npm init -y"
RUN "npm install react typescript express --save"
RUN "Set-Content -Path .gitignore -Value 'node_modules/'"
FINISH for Human Interaction
FINISH PROMPT="Need clarification on payment system. Stripe, PayPal, or both?"
FINISH PROMPT="Structure created! Ready for development phases. Does this look correct?"
FINISH PROMPT="Project completed! Ready for your review."
Phase-Based Workflows
Phase 1: Product Understanding
UPDATE_DOCUMENTATION CONTENT="# Project (DRAFT)\n\n## Questions\n- Target audience?\n- Core features?\n- Platform (web/mobile)?\n- Scale expectations?"

FINISH PROMPT="What's your target audience and core features for this social media app?"

UPDATE_DOCUMENTATION CONTENT="# Requirements v2\n\n## Confirmed\n- Young professionals\n- Web-first\n- Posts/networking\n\n## Need Clarification\n- Auth method?\n- Content types?"

FINISH PROMPT="For auth: email/password or OAuth? What content types: text/images/video?"

UPDATE_DOCUMENTATION CONTENT="# Final Requirements\n\n## Product\nProfessional networking platform\n\n## Features\n- Profiles\n- Posts (text/images)\n- Connections\n- Messaging\n\n## Tech\n- React/TypeScript\n- Node.js/Express\n- PostgreSQL\n- JWT + OAuth"

FINISH PROMPT="Requirements documented. Ready for Phase 2 (Structure Setup)?"
Phase 2: Structure Stage
RUN "New-Item -ItemType Directory -Path src/components -Force"
RUN "New-Item -ItemType Directory -Path src/services -Force"
RUN "New-Item -ItemType Directory -Path src/types -Force"
RUN "New-Item -ItemType File -Path src/types/user.interface.ts"
RUN "New-Item -ItemType File -Path src/services/auth.service.ts"
RUN "New-Item -ItemType File -Path src/services/auth.test.ts"

RUN "npm init -y"
RUN "npm install react typescript express jest --save-dev"

RUN "Set-Content -Path tsconfig.json -Value '{\"compilerOptions\":{\"target\":\"ES2020\",\"strict\":true}}'"
RUN "Set-Content -Path .gitignore -Value 'node_modules/\ndist/\n.env'"

UPDATE_DOCUMENTATION CONTENT="## Environment Guide\n- Build: npm run build\n- Test: npm test\n- Run: npm start"

FINISH PROMPT="Structure complete. Tests adjacent to implementations. Ready for Phase 3?"
Phase 3: Implementation
DELEGATE PROMPT="Phase 1: Core interfaces - user.interface.ts, post.interface.ts with full OOP design"

UPDATE_DOCUMENTATION CONTENT="Phase 1 Complete: All core TypeScript interfaces implemented"

DELEGATE PROMPT="Phase 2: Authentication - auth.service.ts with tests, JWT implementation"

UPDATE_DOCUMENTATION CONTENT="Phase 2 Complete: Authentication system fully tested and secure"

DELEGATE PROMPT="Phase 3: User management - profile CRUD with full test coverage"

UPDATE_DOCUMENTATION CONTENT="Phase 3 Complete: User management operational"

DELEGATE PROMPT="Phase 4: Social features - posts, connections, real-time updates"

UPDATE_DOCUMENTATION CONTENT="Phase 4 Complete: Social features integrated"

DELEGATE PROMPT="Phase 5: Frontend - React components, responsive design, state management"

UPDATE_DOCUMENTATION CONTENT="# COMPLETED\n\n## Delivered\n- Auth system\n- User profiles\n- Posts/connections\n- Real-time messaging\n- 95% test coverage"

FINISH PROMPT="Platform complete! All features implemented with tests. Ready for review?"
Common Patterns
Initial Project Setup
// Phase 1 Loop
UPDATE_DOCUMENTATION CONTENT="# Understanding v1..."
FINISH PROMPT="What problem are we solving?"
UPDATE_DOCUMENTATION CONTENT="# Understanding v2..."
FINISH PROMPT="What are the success metrics?"
// Continue until approval...

// Phase 2 Setup
RUN "New-Item -ItemType Directory -Path src -Force"
RUN "npm init -y"
RUN "npm install typescript --save-dev"
FINISH PROMPT="Environment ready. Proceed?"

// Phase 3 Delegation
DELEGATE PROMPT="Build foundation with tests"
UPDATE_DOCUMENTATION CONTENT="Foundation complete"
DELEGATE PROMPT="Implement business logic"
UPDATE_DOCUMENTATION CONTENT="Business logic complete"
FINISH PROMPT="Complete! Review?"
Reading and Verification
READ file "documentation.md"
READ folder "src", folder "test"
READ file "package.json", file "tsconfig.json"
Documentation Updates
UPDATE_DOCUMENTATION CONTENT="# Phase 1 Complete\n- Interfaces defined\n- Tests written\n- Ready for implementation"

UPDATE_DOCUMENTATION CONTENT="# Final Status\n- All tests passing\n- Features complete\n- Production ready"
Error Handling
// After delegation completes, if issues found
READ folder "src/services"
UPDATE_DOCUMENTATION CONTENT="# Issue Found\nPerformance problem in auth service"
DELEGATE PROMPT="Optimize auth service - implement caching, reduce DB queries"

// Scope change
UPDATE_DOCUMENTATION CONTENT="# Scope Update\nAdded real-time chat requirement"
FINISH PROMPT="New chat feature affects architecture. Redesign for WebSockets?"
Quick Reference
// Phase transitions
FINISH PROMPT="Phase 1 complete. Proceed to Phase 2?"
FINISH PROMPT="Structure ready. Begin implementation?"
FINISH PROMPT="Project complete. Does this meet requirements?"

// Common delegations
DELEGATE PROMPT="Implement interfaces with OOP principles"
DELEGATE PROMPT="Build service layer with full test coverage"
DELEGATE PROMPT="Create frontend with responsive design"

// Structure creation
RUN "New-Item -ItemType Directory -Path [path] -Force"
RUN "New-Item -ItemType File -Path [filepath]"
RUN "Set-Content -Path [file] -Value '[content]'"

// Package management
RUN "npm install [packages] --save"
RUN "npm install [packages] --save-dev"

// Always remember
UPDATE_DOCUMENTATION CONTENT="..."  // Track progress
FINISH PROMPT="..."  // Get human approval between phases