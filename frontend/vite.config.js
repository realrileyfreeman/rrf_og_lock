import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/decode": "http://localhost:8000",
      "/decodeurs": "http://localhost:8000",
    },
  },
});
