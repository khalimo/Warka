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

export async function generateMetadata({ params }: StoryPageProps) {
  const story = await apiClient.getStory(params.slug)

  if (!story) {
    return { title: 'Story Not Found' }
  }

  return {
    title: story.title,
    description: story.excerpt,
  }
}

export default async function StoryPage({ params }: StoryPageProps) {
  const story = await apiClient.getStory(params.slug)

  if (!story) {
    notFound()
  }

  return (
    <article className="container-custom py-12">
      <div className="mx-auto max-w-3xl">
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
            <img src={story.imageUrl} alt={story.title} className="h-auto w-full" />
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
            className="text-primary-600 hover:underline"
          >
            Read original story on {story.source.name} →
          </Link>
        </div>
      </div>
    </article>
  )
}
