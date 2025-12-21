import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: "/podagent/",   // <-- IMPORTANT for GitHub Pages (repo name)
  plugins: [react()],
});
