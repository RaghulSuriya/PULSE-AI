/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ["images.unsplash.com", "lh3.googleusercontent.com"],
  },
  async rewrites() {
    const backendUrl = (process.env.NEXT_PUBLIC_API_URL || process.env.BACKEND_URL || "http://localhost:8000").replace(/\/$/, "");
    // If backendUrl already includes /api/v1, strip it so destination formats cleanly
    const targetBase = backendUrl.endsWith("/api/v1") ? backendUrl.slice(0, -7) : backendUrl;
    return [
      {
        source: "/api/v1/:path*",
        destination: `${targetBase}/api/v1/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
