import Link from 'next/link'
import { Story } from '@/lib/types'
import { StoryMeta } from './StoryMeta'

export function StoryCardLarge({ story }: { story: Story }) {
  return (
    <Link href={`/story/${story.slug}`} className="group block">
      <article className="overflow-hidden rounded-lg border border-gray-200 bg-white transition-shadow hover:shadow-md">
        {story.imageUrl ? (
          <img src={story.imageUrl} alt={story.title} className="h-48 w-full object-cover transition-transform duration-300 group-hover:scale-[1.02]" />
        ) : null}
        <div className="p-4">
          <h3 className="font-serif text-xl font-bold text-gray-900 transition-colors group-hover:text-primary-600">
            {story.title}
          </h3>
          <p className="mt-2 line-clamp-2 text-sm leading-6 text-gray-600">{story.excerpt}</p>
          <StoryMeta story={story} compact />
        </div>
      </article>
    </Link>
  )
}
