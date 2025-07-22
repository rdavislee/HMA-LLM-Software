import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./components"),
    },
  },
  server: {
    port: 3001,
    host: true
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate vendor chunks for better caching
          react: ['react', 'react-dom'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-select', '@radix-ui/react-tabs'],
          utils: ['clsx', 'tailwind-merge']
        }
      }
    },
    // Reduce chunk size warning threshold since our app is feature-rich
    chunkSizeWarningLimit: 1000
  }
})