import { defineConfig } from 'vite';
import { fileURLToPath } from 'node:url';
export default defineConfig({
  optimizeDeps: { entries: ['index.html', 'viewer.html'] },
  base: './', server: { port: 5173, strictPort: true },
  build: { chunkSizeWarningLimit: 800, rollupOptions: { input: {
    home: fileURLToPath(new URL('./index.html', import.meta.url)),
    viewer: fileURLToPath(new URL('./viewer.html', import.meta.url)),
  } } },
});
