import { EmptyState } from '@/components/ui/EmptyState'
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { StoryCardCompact } from '@/components/story/StoryCardCompact'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'Latest Stories',
  description: 'The latest reporting from Warka across Somalia and the wider world.',
}

export const dynamic = 'force-dynamic'

export default async function LatestPage() {
  const result = await apiClient.getLatestStories(50, 0)

  if (!result) {
    return (
      <div className="container-custom py-12">
        <LoadingSkeleton variant="list" count={6} />
        <div className="mt-8">
          <EmptyState
            title="We couldn&apos;t load the latest stories"
            message="The latest feed is temporarily unavailable. Please try again shortly."
          />
        </div>
      </div>
    )
  }

  if (result.items.length === 0) {
    return (
      <div className="container-custom py-12">
        <EmptyState title="No stories yet" message="Ingestion may still be running." />
      </div>
    )
  }

  return (
    <div className="container-custom py-12">
      <SectionHeader title="Latest Stories" subtitle="The newest reporting from Warka's source network." />
      <div className="space-y-1">
        {result.items.map((story) => (
          <StoryCardCompact key={story.id} story={story} />
        ))}
      </div>
    </div>
  )
}
