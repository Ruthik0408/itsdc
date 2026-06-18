import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    watch: {
      ignored: [
        '**/venv/**',
        '**/__pycache__/**',
        '**/dist/**',
        '**/node_modules/**',
        '**/*.pyc',
      ],
    },
  },
});
