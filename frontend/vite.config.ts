import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    hmr: {
      // Reducir la frecuencia de pings (por defecto es 1000ms)
      pingInterval: 5000, // Cambiar a 5 segundos
      // O desactivar completamente los pings
      // pingInterval: false
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
