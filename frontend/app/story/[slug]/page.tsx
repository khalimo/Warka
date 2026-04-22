import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import { apiClient } from '@/lib/api'
import { SourceBadge } from '@/components/story/SourceBadge'
import { FramingBadge } from '@/components/story/FramingBadge'
import { TimeAgo } from '@/components/ui/TimeAgo'

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
    <article className="container-custom py-12">
      <div className="mx-auto max-w-3xl">
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
        <div className="mb-4 flex flex-wrap gap-3">
          <SourceBadge source={story.source} />
          {story.framing ? <FramingBadge framing={story.framing} /> : null}
        </div>

        <h1 className="mb-4 text-3xl font-bold md:text-4xl lg:text-5xl">{story.title}</h1>

        {story.excerpt ? <p className="mb-6 text-xl leading-relaxed text-gray-600">{story.excerpt}</p> : null}

        <div className="mb-8 flex items-center gap-4 border-y border-gray-100 py-4 text-sm text-gray-500">
          <span>{story.source.name}</span>
          <span>•</span>
          <TimeAgo date={story.publishedAt} />
          <span>•</span>
          <span>{story.region}</span>
        </div>

        {story.imageUrl ? (
          <div className="mb-8 overflow-hidden rounded-lg">
            <img src={story.imageUrl} alt={story.title} className="h-auto w-full object-cover" />
          </div>
        ) : null}

        {story.summary ? (
          <div className="mb-8 rounded-lg bg-gray-50 p-6">
            <h3 className="mb-2 font-semibold">Summary</h3>
            <p className="text-gray-700">{story.summary}</p>
          </div>
        ) : null}

        {story.content ? (
          <div className="prose prose-lg max-w-none" dangerouslySetInnerHTML={{ __html: story.content }} />
        ) : null}

        <div className="mt-8 border-t border-gray-200 pt-6">
          <Link
            href={story.originalUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center rounded-full bg-primary-50 px-4 py-2 font-medium text-primary-700 transition-colors hover:bg-primary-100"
          >
            Read original story on {story.source.name} →
          </Link>
        </div>
      </div>
    </article>
  )
}
