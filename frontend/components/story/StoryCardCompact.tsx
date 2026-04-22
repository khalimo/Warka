'use client'

import Link from 'next/link'
import { Story } from '@/lib/types'
import { StoryMeta } from './StoryMeta'
import { useLanguage } from '@/components/language/LanguageProvider'
import { getStoryExcerpt, getStoryHeadline } from '@/lib/storyPresentation'

export function StoryCardCompact({ story }: { story: Story }) {
  const { lang, dictionary } = useLanguage()

  return (
    <Link href={`/story/${story.slug}`} className="group block editorial-link px-3.5 py-3.5 first:pt-4 last:pb-4 sm:px-5 sm:py-4 sm:first:pt-5 sm:last:pb-5">
      <div className="flex gap-3.5 sm:gap-5">
        {story.imageUrl ? (
          <img
            src={story.imageUrl}
            alt={getStoryHeadline(story, lang)}
            className="h-20 w-20 rounded-editorial object-cover transition-transform duration-300 ease-editorial group-hover:scale-[1.02] sm:h-28 sm:w-28"
          />
        ) : (
          <div className="flex h-20 w-20 items-center justify-center rounded-editorial border border-[#ddd0c0] bg-paper px-2 text-center text-[0.62rem] font-semibold uppercase tracking-[0.16em] text-ink/35 dark:border-white/10 dark:bg-[#182124] dark:text-[#a8a39b] sm:h-28 sm:w-28 sm:text-[0.66rem] sm:tracking-[0.18em]">
            {dictionary.brand.name}
          </div>
        )}
        <div className="min-w-0 flex-1">
          <h3 className="font-serif text-[1.05rem] font-bold leading-[1.12] text-ink transition-colors duration-300 ease-editorial group-hover:text-primary-600 dark:text-[#fbf7f0] dark:group-hover:text-primary-200 sm:text-lg">
            {getStoryHeadline(story, lang)}
          </h3>
          <p className="mt-1.5 line-clamp-2 text-sm leading-6 text-ink/66 dark:text-[#cbc5bc] sm:mt-2 sm:leading-7">
            {getStoryExcerpt(story, lang)}
          </p>
          <StoryMeta story={story} compact />
        </div>
      </div>
    </Link>
  )
}
