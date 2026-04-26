'use client'

import clsx from 'clsx'
import { useLanguage } from '@/components/language/LanguageProvider'
import { hasStoryTranslation, isOriginalStoryLanguage } from '@/lib/storyPresentation'
import { Story } from '@/lib/types'

export function StoryTranslationStatus({
  story,
  compact = false,
}: {
  story: Story
  compact?: boolean
}) {
  const { lang, dictionary } = useLanguage()
  const original = isOriginalStoryLanguage(story, lang)
  const translated = !original && hasStoryTranslation(story, lang)
  const label = original
    ? dictionary.translation.original
    : translated
      ? dictionary.translation.translated
      : dictionary.translation.unavailable

  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full border font-semibold uppercase',
        compact
          ? 'px-2.5 py-1 text-[0.62rem] tracking-[0.1em]'
          : 'px-3 py-1.5 text-[0.7rem] tracking-[0.12em]',
        original
          ? 'border-[#d8cab7] bg-white/80 text-ink/58 dark:border-white/10 dark:bg-[#182124] dark:text-[#bdb6ad]'
          : translated
            ? 'border-primary-200 bg-primary-50 text-primary-700 dark:border-primary-900/60 dark:bg-primary-900/20 dark:text-primary-200'
            : 'border-acacia/30 bg-acacia/10 text-acacia dark:border-acacia/20 dark:bg-acacia/10'
      )}
      title={dictionary.translation.helper}
    >
      {label}
    </span>
  )
}
