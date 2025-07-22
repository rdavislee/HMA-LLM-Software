// Setup import.meta mock
global.import = {
  meta: {
    env: {
      VITE_WS_URL: 'ws://localhost:8080'
    }
  }
};