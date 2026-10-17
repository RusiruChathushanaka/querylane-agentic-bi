import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  // Keep optional local previews/build checks separate from another running dev server.
  distDir: process.env.QUERYLANE_NEXT_DIST_DIR || ".next",
  reactCompiler: true,
  async redirects() {
    return [
      {
        source: "/",
        has: [{ type: "query" as const, key: "chat" }],
        destination: "/app",
        permanent: false,
      },
    ];
  },
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
