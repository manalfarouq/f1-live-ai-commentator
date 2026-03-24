import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/video': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/prediction': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/commentary': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/chat': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
})