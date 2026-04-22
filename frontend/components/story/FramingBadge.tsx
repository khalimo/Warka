import { Framing } from '@/lib/types'

interface FramingBadgeProps {
  framing: Framing
  size?: 'sm' | 'md'
}

export function FramingBadge({ framing, size = 'md' }: FramingBadgeProps) {
  const sizeClasses =
    size === 'sm'
      ? 'px-2.5 py-1 text-[0.68rem] tracking-[0.14em]'
      : 'px-3 py-1.5 text-[0.72rem] tracking-[0.14em]'

  const toneColors = {
    positive:
      'border border-acacia/25 bg-acacia/10 text-acacia dark:border-acacia/20 dark:bg-acacia/10 dark:text-[#ced8bd]',
    neutral:
      'border border-[#d8cab7] bg-white/80 text-ink/72 dark:border-white/10 dark:bg-[#182124] dark:text-[#e7e1d8]',
    negative:
      'border border-primary-200 bg-primary-50/70 text-primary-700 dark:border-primary-900/50 dark:bg-primary-900/20 dark:text-primary-200',
    mixed:
      'border border-sky/25 bg-sky/10 text-sky dark:border-sky/20 dark:bg-sky/10 dark:text-[#d2e4e8]',
  }

  return (
    <span
      className={`inline-flex items-center rounded-full font-semibold uppercase ${toneColors[framing.tone]} ${sizeClasses}`}
    >
      {framing.label}
    </span>
  )
}
