import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Backend proxy target — override via VITE_BACKEND_URL env var
const BACKEND_URL = process.env.VITE_BACKEND_URL || "http://backend:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      "/api": {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      "/static": {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      "/media": {
        target: BACKEND_URL,
        changeOrigin: true,
      },
    },
    watch: {
      usePolling: true,
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
  },
});
