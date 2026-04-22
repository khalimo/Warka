'use client'

import clsx from 'clsx'
import { Story } from '@/lib/types'
import { useLanguage } from '@/components/language/LanguageProvider'

export function StoryLanguageBadge({ story, compact = false }: { story: Story; compact?: boolean }) {
  const { dictionary } = useLanguage()
  const isSomali = story.lang === 'so'

  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full border font-semibold uppercase',
        compact
          ? 'px-2.5 py-1 text-[0.64rem] tracking-[0.12em]'
          : 'px-3 py-1.5 text-[0.72rem] tracking-[0.14em]',
        isSomali
          ? 'border-[#cda771] bg-[#f4dfc7] text-[#8f4a19] dark:border-[#926036] dark:bg-[#3a291b] dark:text-[#f1ca9d]'
          : 'border-[#b8ced9] bg-[#e8f1f5] text-[#1d5d78] dark:border-[#2d5665] dark:bg-[#18252d] dark:text-[#9dd1e4]'
      )}
      aria-label={`${dictionary.accessibility.storyLanguage}: ${
        isSomali ? dictionary.languages.so : dictionary.languages.en
      }`}
    >
      {isSomali ? dictionary.languages.shortSo : dictionary.languages.shortEn}
    </span>
  )
}
