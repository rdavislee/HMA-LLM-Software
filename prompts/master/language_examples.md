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

## Machine Learning Model Training (NO_TIMEOUT)
**CRITICAL**: Only use NO_TIMEOUT for machine learning model training. Never for tests or regular development tasks.

### ✅ Correct NO_TIMEOUT Usage (ML Training Only)
RUN NO_TIMEOUT "python train_model.py --epochs 100 --batch-size 32 --learning-rate 0.001"
RUN NO_TIMEOUT "python -m transformers.trainer --model-name bert-base-uncased --train-file dataset.json --output-dir ./models"
RUN NO_TIMEOUT "python train_neural_network.py --dataset large_dataset.csv --model-type cnn --epochs 500"
RUN NO_TIMEOUT "python -c \"import tensorflow as tf; model = tf.keras.models.load_model('model.h5'); model.fit(train_data, epochs=200)\""

### ❌ NEVER Use NO_TIMEOUT For
RUN "npm test"  // Correct - use normal timeout, divide tests if needed
RUN "python -m pytest tests/"  // Correct - divide test suites instead
RUN "npm run build"  // Correct - build should be fast
RUN "docker build -t myapp ."  // Correct - optimize build if slow

### Test Case Timeout Solutions
Instead of NO_TIMEOUT, divide tests:
RUN "npm test -- --testNamePattern='unit'"
RUN "npm test -- --testNamePattern='integration'"
RUN "npm test -- --testNamePattern='api'"
RUN "python -m pytest tests/unit/"
RUN "python -m pytest tests/integration/"
RUN "python -m pytest tests/performance/"
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

## Machine Learning Project Workflow
Complete example showing proper NO_TIMEOUT usage for ML model training:

### Phase 1: ML Product Understanding
UPDATE_DOCUMENTATION CONTENT="# ML Image Classification System\n\n## Product Vision\nBuild a deep learning system to classify medical images\n\n## Requirements\n- CNN model for image classification\n- 95% accuracy target\n- Real-time inference API\n- Training on 100k+ images\n\n## Tech Stack\n- Python/TensorFlow\n- FastAPI for serving\n- PostgreSQL for metadata\n- Docker for deployment"

FINISH PROMPT="ML requirements documented. Training dataset size: 100k images. Ready for Phase 2?"

### Phase 2: ML Environment Setup
RUN "New-Item -ItemType Directory -Path src/models -Force"
RUN "New-Item -ItemType Directory -Path src/training -Force"
RUN "New-Item -ItemType Directory -Path src/inference -Force"
RUN "New-Item -ItemType Directory -Path data -Force"

RUN "python -m venv ml_env"
RUN ".\\ml_env\\Scripts\\activate"
RUN "pip install tensorflow keras numpy pandas matplotlib scikit-learn"
RUN "pip install fastapi uvicorn pytest"
RUN "pip freeze > requirements.txt"

UPDATE_DOCUMENTATION CONTENT="## Environment Guide\n- Train Model: python src/training/train.py\n- Test: python -m pytest\n- Serve API: python src/inference/api.py"

FINISH PROMPT="ML environment ready. TensorFlow installed. Ready for Phase 3?"

### Phase 3: ML Implementation (Delegation + Training)
DELEGATE PROMPT="Phase 1: Build CNN model architecture in src/models/cnn_model.py with proper OOP design and unit tests"

UPDATE_DOCUMENTATION CONTENT="Phase 1 Complete: CNN architecture implemented with 5 layers, dropout, batch normalization"

DELEGATE PROMPT="Phase 2: Implement data preprocessing pipeline in src/training/data_processor.py with augmentation and validation"

UPDATE_DOCUMENTATION CONTENT="Phase 2 Complete: Data pipeline handles image loading, augmentation, train/val splits"

DELEGATE PROMPT="Phase 3: Create training script structure in src/training/train.py - prepare for model training but don't execute training"

UPDATE_DOCUMENTATION CONTENT="Phase 3 Complete: Training script ready with hyperparameter configuration, checkpointing, logging"

// NOW MASTER AGENT EXECUTES TRAINING (ONLY AGENT AUTHORIZED)
RUN NO_TIMEOUT "python src/training/train.py --epochs 100 --batch-size 32 --learning-rate 0.001 --dataset data/medical_images"

UPDATE_DOCUMENTATION CONTENT="Training Complete: Model achieved 96.2% accuracy on validation set after 100 epochs"

DELEGATE PROMPT="Phase 4: Implement inference API in src/inference/api.py with FastAPI and model serving"

UPDATE_DOCUMENTATION CONTENT="Phase 4 Complete: REST API serving trained model with /predict endpoint"

// Test the complete system (normal timeout)
RUN "python -m pytest src/models/test_cnn_model.py"
RUN "python -m pytest src/training/test_data_processor.py"
RUN "python -m pytest src/inference/test_api.py"

FINISH PROMPT="ML system complete! 96.2% accuracy achieved. API serving predictions. Ready for deployment?"

### Phase 2: ML Environment Examples
Python ML Setup:
RUN "pip install tensorflow torch torchvision"
RUN "pip install scikit-learn pandas numpy matplotlib seaborn"
RUN "pip install jupyter notebook ipykernel"
RUN "pip install transformers datasets"

R ML Setup:
RUN "R -e \"install.packages(c('caret', 'randomForest', 'e1071', 'rpart'))\""
RUN "R -e \"install.packages(c('ggplot2', 'dplyr', 'tidyr'))\""

### Training vs Testing Command Examples
Training Commands (NO_TIMEOUT):
RUN NO_TIMEOUT "python train_cnn.py --epochs 200 --dataset large_images/"
RUN NO_TIMEOUT "python fine_tune_bert.py --model bert-base --train-file data.json --epochs 50"
RUN NO_TIMEOUT "R -e \"source('train_random_forest.R'); train_model(epochs=1000)\""

Testing Commands (Normal Timeout):
RUN "python -m pytest tests/test_model_architecture.py"
RUN "python -m pytest tests/test_preprocessing.py -v"
RUN "python test_inference_speed.py"  // Should complete quickly
RUN "python validate_model_accuracy.py"  // Validation, not training
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