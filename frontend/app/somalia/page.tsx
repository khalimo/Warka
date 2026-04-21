import { EmptyState } from '@/components/ui/EmptyState'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { StoryCardLarge } from '@/components/story/StoryCardLarge'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'Somalia',
  description: 'Essential reporting from across Somalia, gathered in one place.',
}

export default async function SomaliaPage() {
  const result = await apiClient.getSomaliaStories(30, 0)

  if (!result || result.items.length === 0) {
    return (
      <div className="container-custom py-12">
        <EmptyState title="No Somalia stories yet" message="Check back soon." />
      </div>
    )
  }

  return (
    <div className="container-custom py-12">
      <SectionHeader
        title="Somalia"
        subtitle="Essential reporting from across the country, gathered into one clean front page."
      />
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {result.items.map((story) => (
          <StoryCardLarge key={story.id} story={story} />
        ))}
      </div>
    </div>
  )
}
