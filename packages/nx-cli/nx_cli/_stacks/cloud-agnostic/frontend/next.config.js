/** @type {import('next').NextConfig} */
// `output: standalone` produces a self-contained server (server.js) so the
// production image is tiny and cloud-agnostic — runs on any Docker host.
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
};

module.exports = nextConfig;
