import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

// Use environment variables for proxy target; falls back to localhost.
export default ({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiBase = env.VITE_API_BASE || 'http://localhost:8000'

  return defineConfig({
    plugins: [react()],
    server: {
      proxy: {
        '/api': {
          target: apiBase,
          changeOrigin: true,
        },
      },
    },
  })
}
