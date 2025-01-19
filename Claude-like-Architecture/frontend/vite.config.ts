import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { loadEnv } from 'vite';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on mode
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          ws: true,
        },
      },
      host: true,
    },
    build: {
      sourcemap: true,
      rollupOptions: {
        output: {
          manualChunks: {
            react: ['react', 'react-dom'],
            lucide: ['lucide-react'],
            recharts: ['recharts'],
          },
        },
      },
    },
    define: {
      // Expose env variables to the client
      'process.env.VITE_API_BASE_URL': JSON.stringify(env.VITE_API_BASE_URL),
      'process.env.VITE_WS_BASE_URL': JSON.stringify(env.VITE_WS_BASE_URL),
      'process.env.VITE_AI_PROVIDER': JSON.stringify(env.VITE_AI_PROVIDER),
      'process.env.VITE_AI_MODEL': JSON.stringify(env.VITE_AI_MODEL),
    },
  };
});