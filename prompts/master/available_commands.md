Available Commands for Master Agent
⚠️ ELEVATED PRIVILEGES WARNING ⚠️
You have full system access - use responsibly. Always verify paths before destructive operations. Your setup in Phase 2 determines the success of all child agents.
Phase-Based Command Access

Phase 1: READ, UPDATE_DOCUMENTATION, FINISH only
Phase 2: Full terminal access for environment setup
Phase 3: DELEGATE becomes available for implementation

Language Environment Setup Examples
TypeScript/Node.js Projects
Initial Setup:
powershell# Create project structure
RUN "New-Item -ItemType Directory -Path src/components -Force"
RUN "New-Item -ItemType Directory -Path src/services -Force"
RUN "New-Item -ItemType Directory -Path src/types -Force"

# Initialize project
RUN "npm init -y"

# Install TypeScript and build tools
RUN "npm install --save-dev typescript @types/node ts-node tsx"
RUN "npm install --save-dev jest @types/jest ts-jest"
RUN "npm install --save-dev mocha chai @types/mocha @types/chai"

# Install common libraries
RUN "npm install express @types/express"
RUN "npm install react react-dom @types/react @types/react-dom"

# Create TypeScript config
RUN "Set-Content -Path tsconfig.json -Value '{\"compilerOptions\":{\"target\":\"ES2020\",\"module\":\"commonjs\",\"strict\":true,\"esModuleInterop\":true,\"skipLibCheck\":true,\"forceConsistentCasingInFileNames\":true,\"outDir\":\"./dist\",\"rootDir\":\"./src\"},\"include\":[\"src/**/*\"],\"exclude\":[\"node_modules\"]}'"

# Set up package.json scripts
RUN "npm pkg set scripts.build=\"tsc\""
RUN "npm pkg set scripts.test=\"jest\""
RUN "npm pkg set scripts.dev=\"tsx watch src/index.ts\""
Commands for Child Agents:

Build: npm run build
Test: npm test
Run: node dist/index.js

Python Projects
Initial Setup:
powershell# Create project structure
RUN "New-Item -ItemType Directory -Path src -Force"
RUN "New-Item -ItemType Directory -Path tests -Force"

# Create virtual environment
RUN "python -m venv venv"
RUN ".\\venv\\Scripts\\activate"

# Install testing and development tools
RUN "pip install pytest pytest-cov pytest-mock"
RUN "pip install flake8 black mypy"
RUN "pip install setuptools wheel"

# Install common libraries
RUN "pip install fastapi uvicorn"
RUN "pip install requests pandas numpy"
RUN "pip install sqlalchemy psycopg2"

# Create requirements.txt
RUN "pip freeze > requirements.txt"

# Create setup.py for package management
RUN "Set-Content -Path setup.py -Value 'from setuptools import setup, find_packages\nsetup(name=\"project\", packages=find_packages())'"
Commands for Child Agents:

Test: python -m pytest -v
Lint: flake8 src/
Type Check: mypy src/
Run: python src/main.py

Java Projects
Initial Setup:
powershell# Create Maven project structure
RUN "New-Item -ItemType Directory -Path src/main/java -Force"
RUN "New-Item -ItemType Directory -Path src/test/java -Force"
RUN "New-Item -ItemType Directory -Path src/main/resources -Force"

# Create pom.xml for Maven
RUN "Set-Content -Path pom.xml -Value '<?xml version=\"1.0\"?><project><modelVersion>4.0.0</modelVersion><groupId>com.example</groupId><artifactId>project</artifactId><version>1.0.0</version><properties><maven.compiler.source>11</maven.compiler.source><maven.compiler.target>11</maven.compiler.target></properties><dependencies><dependency><groupId>junit</groupId><artifactId>junit</artifactId><version>4.13.2</version><scope>test</scope></dependency></dependencies></project>'"

# Or Gradle setup
RUN "gradle init --type java-application"

# Install dependencies (Maven)
RUN "mvn clean install"

# Install dependencies (Gradle)
RUN "gradle build"
Commands for Child Agents:

Build: mvn compile or gradle build
Test: mvn test or gradle test
Run: java -cp target/classes com.example.Main

Common Development Operations
File Operations (PowerShell)
powershell# Create files with content
RUN "Set-Content -Path .gitignore -Value 'node_modules/\n*.log\n.env'"
RUN "Set-Content -Path README.md -Value '# Project Name\n\n## Setup\n1. Install dependencies\n2. Run tests'"

# Multi-line content
RUN "@'\nline 1\nline 2\nline 3\n'@ | Set-Content -Path config.yaml"

# Append to files
RUN "Add-Content -Path .gitignore -Value '.vscode/'"
Environment Configuration
powershell# Create .env files
RUN "Set-Content -Path .env.example -Value 'DATABASE_URL=\nAPI_KEY=\nPORT=3000'"

# Set up CI/CD configs
RUN "New-Item -ItemType Directory -Path .github/workflows -Force"
RUN "Set-Content -Path .github/workflows/test.yml -Value 'name: Tests\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest'"
Documentation Templates
powershell# Create documentation structure
RUN "New-Item -ItemType Directory -Path docs -Force"
RUN "Set-Content -Path docs/API.md -Value '# API Documentation'"
RUN "Set-Content -Path docs/ARCHITECTURE.md -Value '# Architecture Overview'"

# Update main documentation with environment details
UPDATE_DOCUMENTATION CONTENT="## Environment Setup\n\n### Build\n`npm run build`\n\n### Test\n`npm test`\n\n### Development\n`npm run dev`"
Phase 3 Final Verification
At the end of Phase 3, before declaring the project complete, always verify correctness:
TypeScript Projects
powershell# Run full test suite
RUN "npm run build"
RUN "npm test"

# Create and run a REPL verification file
RUN "Set-Content -Path verify.ts -Value 'import { UserService } from \"./src/services/user.service\";\nimport { AuthService } from \"./src/services/auth.service\";\n\nconsole.log(\"Testing basic functionality...\");\nconst userService = new UserService();\nconst authService = new AuthService();\nconsole.log(\"Services initialized successfully!\");'"

RUN "npx tsx verify.ts"
Python Projects
powershell# Run full test suite
RUN "python -m pytest -v --cov=src"

# Create and run a REPL verification file
RUN "Set-Content -Path verify.py -Value 'from src.services.user_service import UserService\nfrom src.services.auth_service import AuthService\n\nprint(\"Testing basic functionality...\")\nuser_service = UserService()\nauth_service = AuthService()\nprint(\"Services initialized successfully!\")'"

RUN "python verify.py"
Java Projects
powershell# Run full test suite
RUN "mvn test"

# Create and run verification
RUN "Set-Content -Path Verify.java -Value 'public class Verify { public static void main(String[] args) { System.out.println(\"Testing basic functionality...\"); new UserService(); new AuthService(); System.out.println(\"Services initialized successfully!\"); } }'"

RUN "javac -cp target/classes Verify.java"
RUN "java -cp .:target/classes Verify"
Best Practices

Always document the commands that child agents will use in documentation.md
Install all dependencies in Phase 2 - child agents cannot install packages
Create helper scripts if commands are complex
Test the environment before moving to Phase 3
Use appropriate package managers for the chosen language
Set up both testing and linting tools for code quality
Always verify the project works at the end of Phase 3 before declaring completion