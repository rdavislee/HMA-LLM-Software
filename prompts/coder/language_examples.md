markdown# Coder Language Examples

## Reading Files
READ "README.md"
READ "src/api/userController.ts"
READ "components/Button.tsx"
READ "utils/validation.py"
READ "config/database.json"

## Changing File Content

### Simple Changes
CHANGE CONTENT = "export const API_VERSION = '2.0';\n"

### Multiline Changes
CHANGE CONTENT = """export function validateEmail(email: string): boolean {
const regex = /^[^\s@]+@[^\s@]+.[^\s@]+$/;
return regex.test(email);
}"""

## Running Commands

### TypeScript Testing (Required Sequence)
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"

### With Options
RUN "node tools/check-typescript.js"  // Check errors without compiling
RUN "node tools/run-mocha.js --grep 'authentication'"
RUN "node tools/run-mocha.js dist/test/api.test.js"

## Complete Workflows

### API Endpoint Implementation
READ "test/userController.test.ts"
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"
CHANGE CONTENT = """export async function getUser(id: string): Promise<User> {
if (!id || !id.match(/^[a-f0-9]{24}$/)) {
throw new Error('Invalid user ID format');
}
const user = await db.users.findById(id);
if (!user) throw new Error('User not found');
return user;
}"""
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"
FINISH PROMPT = "User endpoint implemented with validation"

### React Component Development
READ "test/Button.test.tsx"
READ "components/ButtonInterface.ts"
CHANGE CONTENT = """import React from 'react';
import { ButtonProps } from './ButtonInterface';
export const Button: React.FC<ButtonProps> = ({
label,
onClick,
disabled = false,
variant = 'primary'
}) => {
const className = btn btn-${variant} ${disabled ? 'disabled' : ''};
return (
<button 
         className={className}
         onClick={onClick}
         disabled={disabled}
     >
{label}
</button>
);
};"""
FINISH PROMPT = "Button component implemented with all props"

### Debugging Failed Tests
// ALWAYS gather context first
READ "test/auth.test.ts"
READ "src/middleware/auth.ts"
READ "src/types/auth.types.ts"
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"
// Then make informed changes based on triangulation
CHANGE CONTENT = """// Fixed token validation based on spec..."""
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"
FINISH PROMPT = "Fixed auth middleware: was checking expiry incorrectly"

## Task Types

### SPEC Task (Database Model)
CHANGE CONTENT = """/**

User model for authentication system
@precondition: email must be unique and valid format
@postcondition: password is hashed before storage
@invariant: createdAt <= updatedAt
*/
export interface IUser {
id: string;
email: string;
password: string;  // bcrypt hashed
role: 'user' | 'admin';
createdAt: Date;
updatedAt: Date;
}"""
FINISH PROMPT = "User model specification complete"


### TEST Task (Validation Utils)
READ "src/utils/validation.ts"  // Check spec first
CHANGE CONTENT = """// Test partitions:
// - Valid emails: standard, with dots, with plus
// - Invalid emails: no @, no domain, spaces
// - Edge cases: empty string, null, very long
describe('Email validation', () => {
// Tests covering all partitions...
})"""
FINISH PROMPT = "Email validation tests covering all partitions"

### IMPLEMENT Task (Config Loader)
READ "test/config.test.ts"  // Verify tests exist
CHANGE CONTENT = """export function loadConfig(env: string = 'development'): Config {
const configPath = ./config/${env}.json;
try {
const raw = fs.readFileSync(configPath, 'utf8');
return JSON.parse(raw);
} catch (error) {
throw new Error(Failed to load config for ${env}: ${error.message});
}
}"""
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"
FINISH PROMPT = "Config loader implemented with error handling"

### Reporting Test Issues
READ "test/dateUtils.test.ts"
READ "src/utils/dateUtils.ts"
RUN "node tools/compile-typescript.js"
RUN "node tools/run-mocha.js"
FINISH PROMPT = "Test issue: expects UTC timestamp but implementation returns local time. Spec unclear - need clarification on timezone handling"

## Key Rules
- One command per line
- Always compile before testing TypeScript
- READ context before CHANGE
- FINISH with clear explanation
- For failures: explain what's wrong and why