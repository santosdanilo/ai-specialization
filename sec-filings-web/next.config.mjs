/** @type {import('next').NextConfig} */
const BACKEND_URL = process.env.BACKEND_URL ?? 'http://localhost:8000';

const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/rag',
        destination: `${BACKEND_URL}/rag`,
      },
      {
        source: '/api/agent',
        destination: `${BACKEND_URL}/agent`,
      },
    ];
  },

  httpAgentOptions: {
    keepAlive: true,
  },

  experimental: {
    proxyTimeout: 120000, // 120s
  },
};

export default nextConfig;
