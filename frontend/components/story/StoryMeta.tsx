import { Story } from '@/lib/types'
import { SourceBadge } from './SourceBadge'
import { FramingBadge } from './FramingBadge'
import { TimeAgo } from '@/components/ui/TimeAgo'

export function StoryMeta({ story, compact = false }: { story: Story; compact?: boolean }) {
  return (
    <div className={`flex flex-wrap items-center gap-2 ${compact ? 'mt-2' : 'mt-3'}`}>
      <SourceBadge source={story.source} size={compact ? 'sm' : 'md'} />
      {story.framing ? <FramingBadge framing={story.framing} size="sm" /> : null}
      <span className="text-xs text-gray-500">
        <TimeAgo date={story.publishedAt} />
      </span>
    </div>
  )
}
