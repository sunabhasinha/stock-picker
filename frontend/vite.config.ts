import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "node:path";

// Same-origin rule (ADR-0007): in dev, /api and /auth are PROXIED to the
// FastAPI server - the browser only ever sees one origin, so the M2
// cookie/CSRF model carries over unchanged. No CORS, ever.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { "@": path.resolve(import.meta.dirname, "src") },
  },
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
      "/auth": "http://127.0.0.1:8000",
    },
  },
});
