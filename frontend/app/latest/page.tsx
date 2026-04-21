import { EmptyState } from '@/components/ui/EmptyState'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { StoryCardCompact } from '@/components/story/StoryCardCompact'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'Latest Stories',
  description: 'The latest reporting from Warka across Somalia and the wider world.',
}

export default async function LatestPage() {
  const result = await apiClient.getLatestStories(50, 0)

  if (!result || result.items.length === 0) {
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
