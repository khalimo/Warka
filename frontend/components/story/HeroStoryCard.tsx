import Link from 'next/link'
import { Story } from '@/lib/types'
import { StoryMeta } from './StoryMeta'

export function HeroStoryCard({ story }: { story: Story }) {
  return (
    <Link href={`/story/${story.slug}`} className="group block">
      <div className="grid grid-cols-1 items-center gap-8 lg:grid-cols-2 lg:gap-12">
        {story.imageUrl ? (
          <div>
            <img
              src={story.imageUrl}
              alt={story.title}
              className="h-64 w-full rounded-lg object-cover shadow-editorial transition-transform duration-500 group-hover:scale-[1.02] md:h-96"
            />
          </div>
        ) : null}
        <div>
          <div className="eyebrow mb-3">Lead Story</div>
          <h1 className="text-3xl font-bold text-gray-900 transition-colors group-hover:text-primary-600 md:text-5xl">
            {story.title}
          </h1>
          <p className="mt-4 text-lg leading-8 text-gray-600 md:text-xl">{story.excerpt}</p>
          <StoryMeta story={story} />
        </div>
      </div>
    </Link>
  )
}
