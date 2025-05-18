import {Metadata} from 'next'
import {notFound} from 'next/navigation'
import Script from 'next/script' // Add Script for JSON-LD
import {getPostBySlug, getAllPosts} from '@/lib/api'
import markdownToHtml from '@/lib/markdownToHtml'
import Container from '@/components/blog/_components/container'
import Header from '@/components/blog/_components/header'
import Alert from '@/components/blog/_components/alert'
import {PostHeader} from '@/components/blog/_components/post-header'
import {PostBody} from '@/components/blog/_components/post-body'
import {CMS_NAME} from '@/lib/constants'

// Define the Props type to match Next.js expectations
type Props = {
  params: Promise<{slug: string}> // params is a Promise
}

// Main page component
export default async function Page({params}: Props) {
  const {slug} = await params // Await the params to resolve the slug
  const post = await getPostBySlug(slug)

  if (!post) return notFound()

  const content = await markdownToHtml(post.content || '')

  // Prepare data for JSON-LD
  const canonicalUrl = `https://www.oasispoolsli.com/posts/${post.slug}`
  const seoDescription =
    post.excerpt ||
    'Read our latest article on outdoor and landscape lighting trends, tips, and more.'
  const imageUrl = post.ogImage?.url?.startsWith('http')
    ? post.ogImage.url
    : `https://www.oasispoolsli.com${post.ogImage?.url}`

  return (
    <>
      {/* JSON-LD: BlogPosting */}
      <Script
        id="blogposting-jsonld"
        type="application/ld+json"
        strategy="afterInteractive"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'BlogPosting',
            headline: post.title,
            description: seoDescription,
            image: imageUrl || undefined,
            datePublished: post.date,
            author: {
              '@type': 'Person',
              name: post.author.name,
            },
            publisher: {
              '@type': 'Organization',
              name: CMS_NAME,
              logo: {
                '@type': 'ImageObject',
                url: 'https://www.oasispoolsli.com/images/oasis.png', // Update with your logo URL
              },
            },
            mainEntityOfPage: {
              '@type': 'WebPage',
              '@id': canonicalUrl,
            },
          }),
        }}
      />

      {/* JSON-LD: FAQPage (if FAQ exists) */}
      {post.faq && post.faq.length > 0 && (
        <Script
          id="faqpage-jsonld"
          type="application/ld+json"
          strategy="afterInteractive"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'FAQPage',
              mainEntity: post.faq.map((item) => ({
                '@type': 'Question',
                name: item.question,
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: item.answer,
                },
              })),
            }),
          }}
        />
      )}

      <main>
        <Alert preview={post.preview} />
        <Container>
          <Header />
          <article className="mb-32">
            <PostHeader
              title={post.title}
              coverImage={post.coverImage}
              date={post.date}
              author={post.author}
            />
            <PostBody content={content} faq={post.faq} />
          </article>
        </Container>
      </main>
    </>
  )
}

// Metadata generation
export async function generateMetadata({params}: Props): Promise<Metadata> {
  const {slug} = await params // Await the params to resolve the slug
  const post = await getPostBySlug(slug)
  if (!post) return {}

  const title = `${post.title} | Blog | ${CMS_NAME}`
  const description =
    post.excerpt ||
    'Read our latest article on outdoor and landscape lighting trends, tips, and more.'

  const imageUrl = post.ogImage?.url?.startsWith('http')
    ? post.ogImage.url
    : `https://www.oasispoolsli.com${post.ogImage?.url}`

  return {
    title,
    description,
    alternates: {
      canonical: `https://www.oasispoolsli.com/posts/${post.slug}`,
    },
    openGraph: {
      title,
      description,
      url: `https://www.oasispoolsli.com/posts/${post.slug}`,
      type: 'article',
      images: [
        {
          url: imageUrl,
          width: 1200,
          height: 630,
          alt: post.title,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      images: [imageUrl],
    },
  }
}

// Static params generation
export async function generateStaticParams() {
  const posts = getAllPosts()
  return posts.map((post) => ({
    slug: post.slug,
  }))
}
