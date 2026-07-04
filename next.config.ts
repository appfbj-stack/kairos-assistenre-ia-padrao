import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  output: "standalone",
  transpilePackages: ["@kairos/chat-ui"],
  turbopack: {
    root: process.cwd(),
  },
}

export default nextConfig
