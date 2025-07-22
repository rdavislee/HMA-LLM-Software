# Web App Test Suite

Comprehensive unit tests for the HMA-LLM web application.

## Test Coverage

### ✅ Completed Tests

1. **Services**
   - `websocket.test.ts` - WebSocket service connection, events, and messaging
   - `chatStorage.test.ts` - Local storage operations for chat sessions

2. **Hooks**
   - `useSocketEvent.test.tsx` - WebSocket event listener hook

3. **Components**
   - `AgentBar.test.tsx` - Agent status display and real-time updates
   - `ChatPanel.test.tsx` - Chat message rendering and WebSocket integration
   - `UserInput.test.tsx` - Text input, file attachments, and message sending

### 🚧 Pending Tests

- Terminal component (xterm.js integration)
- FileTree component (file navigation)
- ThreadedChat component (task threading)
- WaveProgress component (progress animations)
- CodeEditor component (Monaco editor)
- ResizableLayout component
- App.tsx integration tests

## Running Tests

```bash
# Install dependencies
npm install

# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch

# Run specific test file
npm test -- __tests__/components/ChatPanel.test.tsx
```

## Test Structure

```
test_web_app/
├── __tests__/
│   ├── components/     # Component tests
│   ├── services/       # Service tests
│   └── hooks/          # Hook tests
├── mocks/              # Mock implementations
├── setup/              # Test setup and utilities
└── coverage/           # Coverage reports
```

## Mocking Strategy

- **WebSocket**: Mocked to avoid import.meta issues
- **Socket.IO**: Custom mock implementation
- **xterm.js**: Mocked terminal functionality
- **localStorage**: In-memory mock
- **Browser APIs**: ResizeObserver, IntersectionObserver, matchMedia

## Test Utilities

- Custom render function with user event setup
- Mock factories for common data structures
- WebSocket event simulation helpers

## Coverage Thresholds

- Branches: 70%
- Functions: 70%
- Lines: 70%
- Statements: 70%

## Known Issues

1. Import.meta environment variables are mocked
2. Some UI library components are excluded from coverage
3. Terminal tests require xterm.js mocking

## Best Practices

1. Use `@testing-library/react` for component testing
2. Mock external dependencies at the module level
3. Test user interactions, not implementation details
4. Maintain test isolation with proper cleanup
5. Use descriptive test names following "should..." pattern