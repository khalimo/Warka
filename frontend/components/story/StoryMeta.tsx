'use client'

import { Story } from '@/lib/types'
import { SourceBadge } from './SourceBadge'
import { FramingBadge } from './FramingBadge'
import { TimeAgo } from '@/components/ui/TimeAgo'
import { StoryLanguageBadge } from './StoryLanguageBadge'
import { StoryTranslationStatus } from './StoryTranslationStatus'
import { useLanguage } from '@/components/language/LanguageProvider'
import { formatReadTime } from '@/lib/i18n'

export function StoryMeta({ story, compact = false }: { story: Story; compact?: boolean }) {
  const { lang } = useLanguage()

  return (
    <div
      className={`flex flex-wrap items-center gap-2 sm:gap-2.5 ${compact ? 'mt-2.5 text-[0.76rem] sm:mt-3 sm:text-[0.78rem]' : 'mt-4 text-[0.82rem] sm:mt-5 sm:text-sm'}`}
    >
      <StoryLanguageBadge story={story} compact={compact} />
      <StoryTranslationStatus story={story} compact={compact} />
      <SourceBadge source={story.source} size={compact ? 'sm' : 'md'} />
      {story.framing ? <FramingBadge framing={story.framing} size="sm" /> : null}
      {story.readingTime ? (
        <span className="text-[0.72rem] font-medium text-ink/56 dark:text-[#c4bdb4] sm:text-[0.76rem]">
          {formatReadTime(story.readingTime, lang)}
        </span>
      ) : null}
      <span className="text-[0.7rem] font-medium uppercase tracking-[0.14em] text-ink/50 dark:text-[#b9b2a8] sm:text-[0.74rem]">
        <TimeAgo date={story.publishedAt} />
      </span>
    </div>
  )
}
