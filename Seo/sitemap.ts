import {NextApiRequest, NextApiResponse} from 'next'
import {towns} from '@/data/towns'
import {getAllPosts} from '@/lib/api'
import {BASE_URL} from '../../../lib/constants'
import fs from 'fs'
import path from 'path'

interface Product {
  slug: string
}

const baseUrl = BASE_URL || 'https://www.oasislightingdesign.com'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const date = new Date().toISOString().split('T')[0]

  // Town Pages with New Route Structure: /towns/[county]/[town]
  const townEntries = towns
    .filter((town) => town.county)
    .map((town) => {
      const countySlug = town
        .county!.toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[^\w-]/g, '')
      return {
        url: `${baseUrl}/towns/${countySlug}/${town.slug}/`,
        lastModified: date,
        changeFrequency: 'monthly',
        priority: 0.8,
      }
    })

  // Blog Posts
  const blogPosts = getAllPosts()
  const blogPostEntries = blogPosts.map((post) => ({
    url: `${baseUrl}/posts/${post.slug}`,
    lastModified: date,
    changeFrequency: 'monthly',
    priority: 0.7,
  }))

  // Lighting Products
  const lightingPath = path.join(process.cwd(), 'public', 'data', 'products.json')
  const lightingProducts = JSON.parse(fs.readFileSync(lightingPath, 'utf8')) as Product[]
  const lightingEntries = lightingProducts.map((product) => ({
    url: `${baseUrl}/products/${product.slug}`,
    lastModified: date,
    changeFrequency: 'monthly',
    priority: 0.75,
  }))

  // Pool Products
  const poolPath = path.join(process.cwd(), 'public', 'data', 'pools.json')
  const poolProducts = JSON.parse(fs.readFileSync(poolPath, 'utf8')) as Product[]
  const poolEntries = poolProducts.map((product) => ({
    url: `${baseUrl}/products/${product.slug}`,
    lastModified: date,
    changeFrequency: 'monthly',
    priority: 0.75,
  }))

  // Static Pages
  const sitemapEntries = [
    {url: baseUrl, lastModified: date, changeFrequency: 'daily', priority: 1.0},
    {url: `${baseUrl}/posts`, lastModified: date, changeFrequency: 'weekly', priority: 0.9},
    {
      url: `${baseUrl}/products/lighting`,
      lastModified: date,
      changeFrequency: 'weekly',
      priority: 0.9,
    },
    {
      url: `${baseUrl}/products/pools`,
      lastModified: date,
      changeFrequency: 'weekly',
      priority: 0.9,
    },
    {url: `${baseUrl}/catalogs`, lastModified: date, changeFrequency: 'weekly', priority: 0.9},
    {url: `${baseUrl}/contact`, lastModified: date, changeFrequency: 'monthly', priority: 0.8},

    // Services
    ...[
      'color-changing-lights',
      'hardscape-lighting',
      'indicator-lights',
      'led-tape-lighting',
      'pendant-lighting',
      'spotlights-flood-lights',
      'walkway-lighting',
      'wall-mounted-lighting',
      'well-lights',
    ].map((slug) => ({
      url: `${baseUrl}/services/${slug}`,
      lastModified: date,
      changeFrequency: 'weekly',
      priority: 0.9,
    })),
    {url: `${baseUrl}/services`, lastModified: date, changeFrequency: 'weekly', priority: 0.9},

    ...townEntries,
    ...blogPostEntries,
    ...lightingEntries,
    ...poolEntries,
  ]

  // 🧾 Build XML
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${sitemapEntries
  .map(
    (entry) => `
  <url>
    <loc>${entry.url}</loc>
    <lastmod>${entry.lastModified}</lastmod>
    <changefreq>${entry.changeFrequency}</changefreq>
    <priority>${entry.priority}</priority>
  </url>`,
  )
  .join('')}
</urlset>`

  res.setHeader('Content-Type', 'application/xml')
  res.setHeader('Cache-Control', 'public, s-maxage=3600, stale-while-revalidate')
  res.status(200).send(xml)
}
