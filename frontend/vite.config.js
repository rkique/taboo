import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 5173,
    allowedHosts: ["6c19-128-148-206-117.ngrok-free.app"],
    proxy: {
      "/socket.io": {
        target: "http://127.0.0.1:5001",
        ws: true,
      },
    },
  },
});
