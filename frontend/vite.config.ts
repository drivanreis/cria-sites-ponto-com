// frontend/vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true, // Importante para o Docker
    allowedHosts: [
      // Adicione o host específico que o ngrok está usando AGORA para o frontend
      // Equivalente localhost:3000
      ...[process.env.VITE_FRONTEND_NGROK_HOST].filter((host): host is string => typeof host === 'string'),
      'localhost',
    ],
  },
  base: '/', // Geralmente bom ter para apps SPA
});