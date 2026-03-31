import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig(({ mode }) => {
  const isAnalyze = mode === 'analyze'

  return {
    plugins: [
      react(),
      isAnalyze
        ? visualizer({
            filename: 'dist/bundle-analysis.html',
            template: 'treemap',
            gzipSize: true,
            brotliSize: true,
            open: false,
          })
        : null,
      isAnalyze
        ? visualizer({
            filename: 'dist/bundle-analysis.json',
            template: 'raw-data',
            gzipSize: true,
            brotliSize: true,
          })
        : null,
    ].filter(Boolean),
    server: {
      host: '0.0.0.0',
      port: 5174,
    },
    build: {
      sourcemap: false,
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (id.includes('node_modules/recharts')) {
              return 'charts'
            }
            if (id.includes('node_modules')) {
              return 'vendor'
            }
          },
        },
      },
    },
  }
})