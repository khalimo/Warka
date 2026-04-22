'use client'

import Link from 'next/link'
import { Story } from '@/lib/types'
import { StoryMeta } from './StoryMeta'
import { useLanguage } from '@/components/language/LanguageProvider'
import { getStoryExcerpt, getStoryHeadline } from '@/lib/storyPresentation'

export function HeroStoryCard({ story }: { story: Story }) {
  const { lang, dictionary } = useLanguage()

  return (
    <Link href={`/story/${story.slug}`} className="group block editorial-link">
      <article className="grid gap-5 sm:gap-8 xl:grid-cols-[minmax(0,0.94fr)_minmax(24rem,1.06fr)] xl:items-end">
        {story.imageUrl ? (
          <div className="order-1 overflow-hidden rounded-editorial border border-[#d7cab9] shadow-editorial dark:border-white/10 xl:order-2">
            <img
              src={story.imageUrl}
              alt={getStoryHeadline(story, lang)}
              className="aspect-[16/10] h-full w-full object-cover transition-transform duration-500 ease-editorial group-hover:scale-[1.02] sm:aspect-[16/10] xl:aspect-[5/6]"
            />
          </div>
        ) : null}
        <div className="order-2 max-w-3xl xl:order-1 xl:pb-4">
          <div className="eyebrow mb-3 sm:mb-4">{dictionary.cards.leadStory}</div>
          <h1 className="max-w-[17ch] text-[2rem] font-bold leading-[0.98] text-ink transition-colors duration-300 ease-editorial group-hover:text-primary-600 dark:text-[#fbf7f0] dark:group-hover:text-primary-200 sm:text-[2.8rem] sm:leading-[0.98] md:text-[3.45rem] xl:text-[4.4rem]">
            {getStoryHeadline(story, lang)}
          </h1>
          <p className="mt-4 max-w-[58ch] text-[1rem] leading-7 text-ink/72 dark:text-[#d4cec5] sm:mt-5 sm:text-[1.04rem] sm:leading-8 md:text-[1.18rem] md:leading-9">
            {getStoryExcerpt(story, lang)}
          </p>
          <StoryMeta story={story} />
        </div>
      </article>
    </Link>
  )
}
