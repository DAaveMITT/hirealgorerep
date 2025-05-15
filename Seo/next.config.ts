import {towns} from './src/data/towns'
import type {NextConfig} from 'next'

type Town = {
  name: string
  county?: string
  slug: string
}

const nextConfig: NextConfig = {
  reactStrictMode: true,
  trailingSlash: true,
  pageExtensions: ['ts', 'tsx', 'js', 'jsx', 'md', 'mdx'],
  images: {
    domains: ['www.oasislightingdesign.com', 'cdn.fluidrausa.com'],
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: `
              default-src 'self';
              script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com https://maps.googleapis.com https://maps.gstatic.com;
              style-src 'self' 'unsafe-inline';
              img-src 'self' data: https: https://www.google-analytics.com https://cdn.fluidrausa.com;
              connect-src 'self' https://www.google-analytics.com https://www.googletagmanager.com https://formspree.io https://play.vidyard.com;
              frame-src https://www.googletagmanager.com https://www.google.com https://maps.google.com;
              font-src 'self';
            `
              .replace(/\s{2,}/g, ' ')
              .trim(),
          },
          {key: 'X-Content-Type-Options', value: 'nosniff'},
          {key: 'X-Frame-Options', value: 'SAMEORIGIN'},
          {key: 'Referrer-Policy', value: 'no-referrer-when-downgrade'},
          {key: 'X-XSS-Protection', value: '1; mode=block'},
        ],
      },
    ]
  },
  async redirects() {
    const redirects = towns
      .filter((town: Town) => town.county)
      .map((town: Town) => {
        const countySlug = town.county!.toLowerCase().replace(/\s+/g, '-')
        return {
          source: `/towns/outdoor-lighting/${town.slug}`,
          destination: `/towns/${countySlug}/${town.slug}`,
          permanent: true,
        }
      })
    return redirects
  },
  async rewrites() {
    return [
      {
        source: '/sitemap.xml',
        destination: '/api/sitemap',
      },
    ]
  },
}

export default nextConfig
