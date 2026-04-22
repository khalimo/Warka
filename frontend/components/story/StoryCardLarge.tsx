'use client'

import Link from 'next/link'
import { Story } from '@/lib/types'
import { StoryMeta } from './StoryMeta'
import { useLanguage } from '@/components/language/LanguageProvider'
import { getStoryExcerpt, getStoryHeadline } from '@/lib/storyPresentation'

export function StoryCardLarge({ story }: { story: Story }) {
  const { lang } = useLanguage()

  return (
    <Link href={`/story/${story.slug}`} className="group block editorial-link">
      <article className="section-surface overflow-hidden transition duration-300 ease-editorial hover:-translate-y-0.5 hover:shadow-editorial">
        {story.imageUrl ? (
          <div className="overflow-hidden">
            <img
              src={story.imageUrl}
              alt={getStoryHeadline(story, lang)}
              className="aspect-[16/11] w-full object-cover transition-transform duration-300 ease-editorial group-hover:scale-[1.02] sm:aspect-[4/3]"
            />
          </div>
        ) : null}
        <div className="p-4 sm:p-5 md:p-6">
          <h3 className="font-serif text-[1.3rem] font-bold leading-[1.08] text-ink transition-colors duration-300 ease-editorial group-hover:text-primary-600 dark:text-[#fbf7f0] dark:group-hover:text-primary-200 sm:text-[1.45rem] sm:leading-[1.04]">
            {getStoryHeadline(story, lang)}
          </h3>
          <p className="mt-2.5 line-clamp-3 text-[0.98rem] leading-7 text-ink/68 dark:text-[#cfc9c0] sm:mt-3">
            {getStoryExcerpt(story, lang)}
          </p>
          <StoryMeta story={story} compact />
        </div>
      </article>
    </Link>
  )
}
