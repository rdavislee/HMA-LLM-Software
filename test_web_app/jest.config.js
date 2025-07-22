module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/__tests__', '<rootDir>/__mocks__'],
  moduleDirectories: ['node_modules', '<rootDir>'],
  testMatch: ['**/__tests__/**/*.test.(ts|tsx)'],
  moduleNameMapper: {
    '^react$': '<rootDir>/../web_app/node_modules/react',
    '^react-dom$': '<rootDir>/../web_app/node_modules/react-dom',
    '^@/services/websocket$': '<rootDir>/__mocks__/@/services/websocket.ts',
    '^@/hooks/useSocketEvent$': '<rootDir>/__mocks__/@/hooks/useSocketEvent.ts',
    '\\.\\./services/websocket$': '<rootDir>/__mocks__/@/services/websocket.ts',
    '\\.\\./hooks/useSocketEvent$': '<rootDir>/__mocks__/@/hooks/useSocketEvent.ts',
    'services/websocket$': '<rootDir>/__mocks__/@/services/websocket.ts',
    'hooks/useSocketEvent$': '<rootDir>/__mocks__/@/hooks/useSocketEvent.ts',
    '^@/(.*)$': '<rootDir>/../web_app/$1',
    '\\.(css|less|scss|sass)$': '<rootDir>/mocks/styleMock.js',
    '\\.(jpg|jpeg|png|gif|svg)$': '<rootDir>/mocks/fileMock.js',
    '^@xterm/xterm$': '<rootDir>/mocks/xterm.js',
    '^@xterm/xterm/css/xterm\\.css$': '<rootDir>/mocks/styleMock.js',
    '^@xterm/addon-fit$': '<rootDir>/mocks/xterm-addon-fit.js',
    '^@xterm/addon-web-links$': '<rootDir>/mocks/xterm-addon-fit.js',
    '^xterm$': '<rootDir>/mocks/xterm.js',
    '^xterm-addon-fit$': '<rootDir>/mocks/xterm-addon-fit.js',
    '^shiki$': '<rootDir>/mocks/shiki.js',
    '^socket.io-client$': '<rootDir>/mocks/socket.io-client.ts'
  },
  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', {
      tsconfig: {
        jsx: 'react-jsx',
        esModuleInterop: true,
        allowSyntheticDefaultImports: true
      }
    }],
    '^.+\\.(js|jsx)$': 'babel-jest'
  },
  transformIgnorePatterns: [
    'node_modules/(?!(socket\\.io-client)/)'
  ],
  setupFiles: ['<rootDir>/setup/setupImportMeta.js'],
  setupFilesAfterEnv: ['<rootDir>/setup/setupTests.ts'],
  testEnvironmentOptions: {
    customExportConditions: ['node', 'node-addons'],
  },
  globals: {
    'import.meta': {
      env: {
        VITE_WS_URL: 'ws://localhost:8080'
      }
    }
  },
  collectCoverageFrom: [
    '../web_app/**/*.{ts,tsx}',
    '!../web_app/**/*.d.ts',
    '!../web_app/node_modules/**',
    '!../web_app/dist/**',
    '!../web_app/main.tsx',
    '!../web_app/vite-env.d.ts',
    '!../web_app/vite.config.ts',
    '!../web_app/postcss.config.js',
    '!../web_app/tailwind.config.js',
    '!../web_app/components/ui/**',
    '!../web_app/imports/**'
  ],
  coverageDirectory: '<rootDir>/coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  },
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  testTimeout: 10000
};