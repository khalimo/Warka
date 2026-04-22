import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { StoryPageClient } from '@/components/pages/StoryPageClient'

interface StoryPageProps {
  params: {
    slug: string
  }
}

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'
export const dynamic = 'force-dynamic'

export async function generateMetadata({ params }: StoryPageProps): Promise<Metadata> {
  const story = await apiClient.getStory(params.slug)

  if (!story) {
    return { title: 'Story Not Found' }
  }

  const description = story.excerpt || story.summary || 'Read the latest reporting from Warka.'
  const storyUrl = `${siteUrl}/story/${story.slug}`

  return {
    title: story.title,
    description,
    alternates: {
      canonical: storyUrl,
    },
    openGraph: {
      title: story.title,
      description,
      type: 'article',
      url: storyUrl,
      images: story.imageUrl ? [{ url: story.imageUrl }] : [],
      publishedTime: story.publishedAt,
    },
    twitter: {
      card: story.imageUrl ? 'summary_large_image' : 'summary',
      title: story.title,
      description,
      images: story.imageUrl ? [story.imageUrl] : [],
    },
  }
}

export default async function StoryPage({ params }: StoryPageProps) {
  const story = await apiClient.getStory(params.slug)

  if (!story) {
    notFound()
  }

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'NewsArticle',
    headline: story.title,
    description: story.excerpt || story.summary,
    datePublished: story.publishedAt,
    dateModified: story.updatedAt || story.publishedAt,
    image: story.imageUrl ? [story.imageUrl] : undefined,
    mainEntityOfPage: `${siteUrl}/story/${story.slug}`,
    publisher: {
      '@type': 'Organization',
      name: 'Warka',
    },
    author: {
      '@type': 'Organization',
      name: story.source.name,
    },
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <StoryPageClient story={story} />
    </>
  )
}
