import { Source } from '@/lib/types'

interface SourceBadgeProps {
  source: Source
  size?: 'sm' | 'md'
}

export function SourceBadge({ source, size = 'md' }: SourceBadgeProps) {
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-sm'

  return (
    <span className={`inline-flex items-center rounded-full bg-gray-100 font-medium text-gray-700 ${sizeClasses}`}>
      {source.name}
    </span>
  )
}
