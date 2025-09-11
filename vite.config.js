import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    outDir: 'static/assets',
    rollupOptions: {
      input: {
        'js/main': 'src/main.js'
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name][extname]',
        cssFileName: 'css/[name][extname]'
      }
    }
  }
});
