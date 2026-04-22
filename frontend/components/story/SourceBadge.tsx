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

  const accent =
    source.category === 'international'
      ? 'bg-sky/70'
      : source.category === 'somali_regional'
        ? 'bg-acacia/80'
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
