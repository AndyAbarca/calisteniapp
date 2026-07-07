import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// host: "0.0.0.0" so the dev server is reachable from other devices on the
// LAN (phone, laptop), not just from inside the container/localhost.
export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
  },
});
