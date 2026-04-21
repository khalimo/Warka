import Link from 'next/link'
import { Story } from '@/lib/types'
import { StoryMeta } from './StoryMeta'

export function StoryCardCompact({ story }: { story: Story }) {
  return (
    <Link href={`/story/${story.slug}`} className="group block border-b border-gray-100 py-4 last:border-b-0">
      <div className="flex gap-4">
        {story.imageUrl ? (
          <img src={story.imageUrl} alt={story.title} className="h-24 w-24 rounded-lg object-cover" />
        ) : (
          <div className="flex h-24 w-24 items-center justify-center rounded-lg bg-gray-100 text-center text-[11px] font-medium uppercase tracking-[0.12em] text-gray-400">
            Warka
          </div>
        )}
        <div className="min-w-0 flex-1">
          <h3 className="font-semibold text-gray-900 transition-colors group-hover:text-primary-600">{story.title}</h3>
          <p className="mt-1 line-clamp-2 text-sm text-gray-600">{story.excerpt}</p>
          <StoryMeta story={story} compact />
        </div>
      </div>
    </Link>
  )
}
