import { fileURLToPath, URL } from 'node:url'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const src = (dir: string) => fileURLToPath(new URL(`./src/${dir}`, import.meta.url))

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    // Mirrors the "paths" in tsconfig.app.json.
    alias: {
      '@modules': src('modules'),
      '@fx': src('fx'),
      '@data': src('data'),
      '@themes': src('themes'),
      '@styles': src('styles'),
    },
  },
})
