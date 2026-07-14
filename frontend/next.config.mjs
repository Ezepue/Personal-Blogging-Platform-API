/** @type {import('next').NextConfig} */
const API_URL = process.env.API_URL ?? "http://localhost:8000";

const nextConfig = {
  async rewrites() {
    return [
      // Uploaded media (covers, avatars) is stored by and served from the
      // FastAPI backend; article/profile records reference it as /media/<file>.
      { source: "/media/:path*", destination: `${API_URL}/media/:path*` },
    ];
  },
};

export default nextConfig;
