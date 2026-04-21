import { Framing } from '@/lib/types'

interface FramingBadgeProps {
  framing: Framing
  size?: 'sm' | 'md'
}

export function FramingBadge({ framing, size = 'md' }: FramingBadgeProps) {
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-sm'

  const toneColors = {
    positive: 'bg-green-50 text-green-700',
    neutral: 'bg-gray-100 text-gray-700',
    negative: 'bg-red-50 text-red-700',
    mixed: 'bg-amber-50 text-amber-700',
  }

  return (
    <span className={`inline-flex items-center rounded-full font-medium ${toneColors[framing.tone]} ${sizeClasses}`}>
      {framing.label}
    </span>
  )
}
