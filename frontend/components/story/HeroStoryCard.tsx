import Link from 'next/link'
import { Story } from '@/lib/types'
import { StoryMeta } from './StoryMeta'

export function HeroStoryCard({ story }: { story: Story }) {
  return (
    <Link href={`/story/${story.slug}`} className="group block editorial-link">
      <article className="grid gap-5 sm:gap-8 xl:grid-cols-[minmax(0,0.88fr)_minmax(24rem,1.12fr)] xl:items-end">
        {story.imageUrl ? (
          <div className="order-1 overflow-hidden rounded-editorial border border-[#d7cab9] shadow-editorial dark:border-white/10 xl:order-2">
            <img
              src={story.imageUrl}
              alt={story.title}
              className="aspect-[6/5] h-full w-full object-cover transition-transform duration-500 ease-editorial group-hover:scale-[1.02] sm:aspect-[5/4] md:aspect-[16/10] xl:aspect-[5/6]"
            />
          </div>
        ) : null}
        <div className="order-2 max-w-3xl xl:order-1 xl:pb-4">
          <div className="eyebrow mb-3 sm:mb-4">Lead Story</div>
          <h1 className="max-w-[15ch] text-[2.15rem] font-bold leading-[0.98] text-ink transition-colors duration-300 ease-editorial group-hover:text-primary-600 dark:text-[#fbf7f0] dark:group-hover:text-primary-200 sm:text-5xl sm:leading-[0.95] md:text-6xl xl:text-7xl">
            {story.title}
          </h1>
          <p className="mt-4 max-w-2xl text-[0.97rem] leading-7 text-ink/72 dark:text-[#d4cec5] sm:mt-5 sm:text-base sm:leading-8 md:text-xl md:leading-9">
            {story.excerpt}
          </p>
          <StoryMeta story={story} />
        </div>
      </article>
    </Link>
  )
}
