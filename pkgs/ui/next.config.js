/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  images: { unoptimized: true },
  eslint: {
    dirs: ["src"],
  },
};

module.exports = nextConfig;
