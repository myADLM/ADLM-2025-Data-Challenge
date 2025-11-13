// net/web/next.config.mjs

/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // Dev: proxy browser /api/* requests to Gateway:3000
    const gw = process.env.GATEWAY_ORIGIN || "http://localhost:3000";
    return [{ source: "/api/:path*", destination: `${gw}/api/:path*` }];
  },
};

export default nextConfig;
