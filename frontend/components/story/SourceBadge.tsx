'use client'

import { Source } from '@/lib/types'

interface SourceBadgeProps {
  source: Source
  size?: 'sm' | 'md'
}

export function SourceBadge({ source, size = 'md' }: SourceBadgeProps) {
  const sizeClasses =
    size === 'sm'
      ? 'gap-1.5 px-2.5 py-1 text-[0.68rem] tracking-[0.12em]'
      : 'gap-2 px-3 py-1.5 text-[0.72rem] tracking-[0.14em]'

  const category = source.category || ''
  const accent =
    category.includes('international') || category.includes('africa')
      ? 'bg-sky/70'
      : category.includes('regional') || category.includes('puntland') || category.includes('somaliland')
        ? 'bg-acacia/80'
        : category.includes('humanitarian')
          ? 'bg-red-400'
          : category.includes('diaspora')
            ? 'bg-purple-400'
            : category.includes('official')
              ? 'bg-ink/70'
              : 'bg-primary-500'

  return (
    <span
      className={`inline-flex items-center rounded-full border border-[#d7cab9] bg-white/90 font-semibold uppercase text-ink/72 dark:border-white/10 dark:bg-[#182124] dark:text-[#ece6dd] ${sizeClasses}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${accent}`} />
      {source.name}
    </span>
  )
}
